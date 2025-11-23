from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ReporteForm, EvidenciaForm
from .models import Reporte, EstadoReporte, PrioridadReporte, Evidencia
import os


@login_required
def crear_reporte(request):
    """Vista para crear un nuevo reporte"""
    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario = request.user
            
            # Asignar estado inicial "Nuevo" automáticamente
            estado_nuevo = EstadoReporte.objects.filter(nombre='Nuevo').first()
            if estado_nuevo:
                reporte.estado = estado_nuevo
            
            # Asignar prioridad por defecto "Media"
            prioridad_media = PrioridadReporte.objects.filter(nombre='Media').first()
            if prioridad_media:
                reporte.prioridad = prioridad_media
            
            reporte.save()
            
            # Procesar archivo de evidencia si se subió
            archivo_evidencia = request.FILES.get('evidencia')
            if archivo_evidencia:
                # Determinar tipo de evidencia
                extension = os.path.splitext(archivo_evidencia.name)[1].lower()
                if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    tipo = 'foto'
                elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                    tipo = 'video'
                else:
                    tipo = 'documento'
                
                # Crear registro de evidencia CON USUARIO
                evidencia = Evidencia(
                    reporte=reporte,
                    tipo_evidencia=tipo,
                    archivo=archivo_evidencia,
                    nombre_archivo=archivo_evidencia.name,
                    tamano_bytes=archivo_evidencia.size,
                    subida_por=request.user,
                    es_evidencia_reparacion=False
                )
                evidencia.save()
            
            messages.success(request, '¡Reporte creado exitosamente!')
            return redirect('reportes:reporte_exitoso', pk=reporte.pk)
    else:
        form = ReporteForm()
    
    return render(request, 'reportes/crear_reporte.html', {
        'form': form
    })

@login_required
def borrar_evidencia_reparacion(request, pk):
    """Permite al técnico borrar sus propias evidencias de reparación"""
    evidencia = get_object_or_404(Evidencia, pk=pk)
    
    # Verificar que sea del técnico actual
    if evidencia.subida_por != request.user:
        messages.error(request, 'No puedes eliminar esta evidencia.')
        return redirect('usuarios:tecnico_home')
    
    reporte_id = evidencia.reporte.pk
    evidencia.delete()
    
    messages.success(request, 'Evidencia eliminada correctamente.')
    return redirect('reportes:cambiar_estado_reporte', pk=reporte_id)


def reporte_exitoso(request, pk):
    """Vista de confirmación después de crear un reporte"""
    reporte = get_object_or_404(Reporte, pk=pk)
    return render(request, 'reportes/reporte_exitoso.html', {
        'reporte': reporte
    })


@login_required
def detalle_reporte(request, pk):
    """Vista para ver el detalle de un reporte"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # Verificar que el usuario sea el dueño o staff
    if reporte.usuario != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver este reporte.')
        return redirect('reportes:mis_reportes')
    
    return render(request, 'reportes/detalle_reporte.html', {
        'reporte': reporte
    })


@login_required
def agregar_evidencia(request, pk):
    """Vista para agregar evidencias a un reporte existente"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # Verificar que el usuario sea el dueño
    if reporte.usuario != request.user:
        messages.error(request, 'No tienes permiso para agregar evidencias a este reporte.')
        return redirect('reportes:mis_reportes')
    
    if request.method == 'POST':
        form = EvidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            evidencia = form.save(commit=False)
            evidencia.reporte = reporte
            evidencia.save()
            
            messages.success(request, 'Evidencia agregada exitosamente.')
            return redirect('reportes:detalle_reporte', pk=reporte.pk)
    else:
        form = EvidenciaForm()
    
    return render(request, 'reportes/agregar_evidencia.html', {
        'form': form,
        'reporte': reporte
    })


def lista_reportes(request):
    """Vista pública de todos los reportes con filtros"""
    reportes = Reporte.objects.all().order_by('-reportado_en')
    
    # Filtros
    busqueda = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    prioridad = request.GET.get('prioridad', '')
    
    if busqueda:
        reportes = reportes.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(direccion__icontains=busqueda)
        )
    
    if estado:
        reportes = reportes.filter(estado__nombre=estado)
    
    if prioridad:
        reportes = reportes.filter(prioridad__nombre=prioridad)
    
    # Paginación
    paginator = Paginator(reportes, 12)
    page = request.GET.get('page')
    reportes_page = paginator.get_page(page)
    
    # Obtener listas para filtros
    estados = EstadoReporte.objects.all()
    prioridades = PrioridadReporte.objects.all()
    
    context = {
        'reportes': reportes_page,
        'estados': estados,
        'prioridades': prioridades,
        'busqueda': busqueda,
        'estado_seleccionado': estado,
        'prioridad_seleccionada': prioridad,
    }
    return render(request, 'reportes/lista_reportes.html', context)

def mapa_reportes(request):
    """Vista del mapa interactivo con todos los reportes"""
    # Solo obtener reportes que tengan coordenadas válidas
    reportes = Reporte.objects.filter(
        latitud__isnull=False,
        longitud__isnull=False
    ).select_related('estado', 'prioridad', 'usuario')
    
    context = {
        'reportes': reportes,
    }
    return render(request, 'reportes/mapa_reportes.html', context)

@login_required
def crear_reporte_desde_mapa(request):
    """Vista para crear un reporte desde el mapa interactivo"""
    if request.method == 'POST':
        # Obtener datos del formulario
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        tipo = request.POST.get('tipo')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        evidencia_archivo = request.FILES.get('evidencia')
        
        # Validar que haya coordenadas
        if not latitud or not longitud:
            messages.error(request, 'Error: No se recibieron las coordenadas.')
            return redirect('reportes:mapa')
        
        # Obtener dirección desde coordenadas (Nominatim)
        try:
            import requests
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitud}&lon={longitud}"
            headers = {'User-Agent': 'MonitoreoCallesBAQ/1.0'}
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()
            direccion = data.get('display_name', f'Lat: {latitud}, Lng: {longitud}')
        except Exception as e:
            print(f"Error obteniendo dirección: {e}")
            direccion = f'Lat: {latitud}, Lng: {longitud}'
        
        # Crear reporte
        reporte = Reporte()
        reporte.usuario = request.user
        reporte.titulo = titulo
        reporte.tipo = tipo
        reporte.descripcion = descripcion
        reporte.latitud = latitud
        reporte.longitud = longitud
        reporte.direccion = direccion
        
        # Asignar estado inicial "Nuevo"
        estado_nuevo = EstadoReporte.objects.filter(nombre='Nuevo').first()
        if estado_nuevo:
            reporte.estado = estado_nuevo
        
        # Asignar prioridad por defecto "Media"
        prioridad_media = PrioridadReporte.objects.filter(nombre='Media').first()
        if prioridad_media:
            reporte.prioridad = prioridad_media
        
        reporte.save()
        
        # Procesar evidencia si se subió
        if evidencia_archivo:
            extension = os.path.splitext(evidencia_archivo.name)[1].lower()
            if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                tipo_ev = 'foto'
            elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                tipo_ev = 'video'
            else:
                tipo_ev = 'documento'
            
            Evidencia.objects.create(
                reporte=reporte,
                tipo_evidencia=tipo_ev,
                archivo=evidencia_archivo,
                nombre_archivo=evidencia_archivo.name,
                tamano_bytes=evidencia_archivo.size,
                subida_por=request.user,
                es_evidencia_reparacion=False
            )
        
        messages.success(request, f'¡Reporte #{reporte.id} creado exitosamente desde el mapa!')
        
        # SOLUCIÓN: Redirigir al mapa con parámetro para centrar en el nuevo reporte
        return redirect(f"/reportes/mapa/?nuevo={reporte.id}&lat={latitud}&lng={longitud}")
    
    return redirect('reportes:mapa')
