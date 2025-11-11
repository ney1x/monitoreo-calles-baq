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
            
            # SE Asignar estado inicial "Nuevo" automáticamente
            estado_nuevo = EstadoReporte.objects.filter(nombre='Nuevo').first()
            if estado_nuevo:
                reporte.estado = estado_nuevo
            
            # SE Asignar prioridad por defecto "Media"
            prioridad_media = PrioridadReporte.objects.filter(nombre='Media').first()
            if prioridad_media:
                reporte.prioridad = prioridad_media
            
            reporte.save()
            
            # SE Procesar archivo de evidencia si se subió
            archivo_evidencia = request.FILES.get('evidencia')
            if archivo_evidencia:
                # SE Determinar tipo de evidencia
                extension = os.path.splitext(archivo_evidencia.name)[1].lower()
                if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    tipo = 'foto'
                elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                    tipo = 'video'
                else:
                    tipo = 'documento'
                
                # SE Crear registro de evidencia
                evidencia = Evidencia(
                    reporte=reporte,
                    tipo_evidencia=tipo,
                    archivo=archivo_evidencia,
                    nombre_archivo=archivo_evidencia.name,
                    tamano_bytes=archivo_evidencia.size
                )
                evidencia.save()
            
            messages.success(request, '¡Reporte creado exitosamente!')
            return redirect('reportes:reporte_exitoso', pk=reporte.pk)
    else:
        form = ReporteForm()
    
    return render(request, 'reportes/crear_reporte.html', {
        'form': form
    })


def reporte_exitoso(request, pk):
    """Vista de confirmación después de crear un reporte"""
    reporte = get_object_or_404(Reporte, pk=pk)
    return render(request, 'reportes/reporte_exitoso.html', {
        'reporte': reporte
    })


@login_required
def mis_reportes(request):
    """Vista para ver los reportes del usuario actual"""
    reportes = Reporte.objects.filter(usuario=request.user).order_by('-reportado_en')
    return render(request, 'reportes/mis_reportes.html', {
        'reportes': reportes
    })


@login_required
def detalle_reporte(request, pk):
    """Vista para ver el detalle de un reporte"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # SE Verificar que el usuario sea el dueño o staff
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
    
    # SE Verificar que el usuario sea el dueño
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
    
    # SE Filtros
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
    
    # SE Paginación
    paginator = Paginator(reportes, 12)
    page = request.GET.get('page')
    reportes_page = paginator.get_page(page)
    
    # SE Obtener listas para filtros
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
    reportes = Reporte.objects.all().select_related('estado', 'prioridad')
    
    context = {
        'reportes': reportes,
    }
    return render(request, 'reportes/mapa_reportes.html', context)
