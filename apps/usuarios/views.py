from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .forms import RegistroForm, LoginForm
from .models import Usuario
from apps.reportes.models import (
    Reporte, Notificacion, EstadoReporte, PrioridadReporte,
    Asignacion, HistorialReporte, Evidencia
)

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            return redirect('usuarios:login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                # SE Registra la fecha de inicio de sesión
                user.registrar_inicio_sesion()

                messages.success(request, f"Bienvenido, {username}.")

                # SE Redirección correcta según roles del modelo
                if user.rol:
                    rol_nombre = user.rol.nombre
                    if rol_nombre == 'Ciudadano':
                        return redirect('usuarios:ciudadano_home')
                    elif rol_nombre == 'Técnico':
                        return redirect('usuarios:tecnico_home')
                    elif rol_nombre == 'Autoridad':
                        return redirect('usuarios:autoridad_home')
                    elif rol_nombre == 'Administrador':
                        return redirect('/admin/')
                
                # SE Si es staff sin rol específico
                if user.is_staff:
                    return redirect('/admin/')
                
                # SE Fallback a ciudadano
                return redirect('usuarios:ciudadano_home')
            else:
                messages.error(request, "Credenciales inválidas.")
        else:
            messages.error(request, "Error en el formulario.")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('usuarios:login')


def home(request):
    """Vista principal - muestra landing page o redirige según rol"""
    # SE Si está autenticado y tiene un parámetro especial, mostrar landing de todos modos
    if request.GET.get('public'):
        reportes_count = Reporte.objects.count()
        return render(request, 'home.html', {
            'reportes_count': reportes_count,
            'show_public': True
        })
    
    if request.user.is_authenticated:
        # SE Redirigir según rol
        if request.user.rol:
            rol_nombre = request.user.rol.nombre
            if rol_nombre == 'Ciudadano':
                return redirect('usuarios:ciudadano_home')
            elif rol_nombre == 'Técnico':
                return redirect('usuarios:tecnico_home')
            elif rol_nombre == 'Autoridad':
                return redirect('usuarios:autoridad_home')
            elif rol_nombre == 'Administrador':
                return redirect('usuarios:autoridad_home')
        
        # SE Si es staff sin rol, ir a admin
        if request.user.is_staff:
            return redirect('usuarios:autoridad_home')
        
        # SE Fallback a ciudadano
        return redirect('usuarios:ciudadano_home')
    
    # SE Mostrar landing page para usuarios no autenticados
    reportes_count = Reporte.objects.count()
    ciudadanos_count = Usuario.objects.filter(rol__nombre='Ciudadano').count()
    casos_resueltos = Reporte.objects.filter(estado__nombre='Resuelto').count()
    tecnicos_count = Usuario.objects.filter(rol__nombre='Técnico').count()
    
    return render(request, 'home.html', {
        'reportes_count': reportes_count,
        'ciudadanos_count': ciudadanos_count,
        'casos_resueltos': casos_resueltos,
        'tecnicos_count': tecnicos_count,
    })


# ==================================================
# VISTAS POR ROL
# ==================================================
@login_required
def ciudadano_home(request):
    """Dashboard para ciudadanos"""
    mis_reportes = Reporte.objects.filter(usuario=request.user).order_by('-reportado_en')[:5]
    
    estadisticas = {
        'total': Reporte.objects.filter(usuario=request.user).count(),
        'nuevos': Reporte.objects.filter(usuario=request.user, estado__nombre='Nuevo').count(),
        'en_proceso': Reporte.objects.filter(
            usuario=request.user, 
            estado__nombre__in=['En Revisión', 'Asignado', 'En Proceso']
        ).count(),
        'resueltos': Reporte.objects.filter(usuario=request.user, estado__nombre='Resuelto').count(),
    }
    
    context = {
        'mis_reportes': mis_reportes,
        'estadisticas': estadisticas,
    }
    return render(request, 'usuarios/ciudadano_home.html', context)


@login_required
def tecnico_home(request):
    """Dashboard para técnicos"""
    # SE Reportes asignados a este técnico con conteo de evidencias
    mis_asignaciones = Reporte.objects.filter(
        asignaciones__tecnico=request.user
    ).select_related('estado', 'prioridad').annotate(
        num_evidencias=Count('evidencias')
    ).distinct().order_by('-reportado_en')[:10]
    
    estadisticas = {
        'asignados': Reporte.objects.filter(asignaciones__tecnico=request.user).count(),
        'en_proceso': Reporte.objects.filter(
            asignaciones__tecnico=request.user,
            estado__nombre='En Proceso'
        ).count(),
        'resueltos_hoy': Reporte.objects.filter(
            asignaciones__tecnico=request.user,
            estado__nombre='Resuelto',
            actualizado_en__date=timezone.now().date()
        ).count(),
    }
    
    context = {
        'mis_asignaciones': mis_asignaciones,
        'estadisticas': estadisticas,
    }
    return render(request, 'usuarios/tecnico_home.html', context)


@login_required
def autoridad_home(request):
    """Dashboard para autoridades"""
    from django.utils import timezone
    from datetime import timedelta
    
    # SE Estadísticas generales
    estadisticas = {
        'total': Reporte.objects.count(),
        'sin_asignar': Reporte.objects.filter(asignaciones__isnull=True).count(),
        'en_proceso': Reporte.objects.filter(estado__nombre='En Proceso').count(),
        'resueltos': Reporte.objects.filter(estado__nombre='Resuelto').count(),
    }
    
    # SE Reportes recientes sin asignar
    reportes_recientes = Reporte.objects.filter(
        asignaciones__isnull=True
    ).select_related('usuario', 'estado', 'prioridad').order_by('-reportado_en')[:10]
    
    # SE Reportes por tipo (tipo es CharField, no ForeignKey)
    reportes_por_tipo = Reporte.objects.values('tipo').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # SE Reportes por prioridad (nivel_gravedad es IntegerField)
    reportes_por_prioridad = Reporte.objects.values('prioridad__nivel_gravedad').annotate(
        total=Count('id')
    ).order_by('-total')
    
    context = {
        'estadisticas': estadisticas,
        'reportes_recientes': reportes_recientes,
        'reportes_por_tipo': reportes_por_tipo,
        'reportes_por_prioridad': reportes_por_prioridad,
    }
    return render(request, 'usuarios/autoridad_home.html', context)


@login_required
def perfil_view(request):
    """Vista del perfil del usuario"""
    context = {}
    
    # SE Si es ciudadano, agregar estadísticas
    if request.user.rol and request.user.rol.nombre == 'Ciudadano':
        from apps.reportes.models import Reporte
        reportes = Reporte.objects.filter(usuario=request.user)
        
        context['estadisticas'] = {
            'total': reportes.count(),
            'nuevos': reportes.filter(estado__nombre='Nuevo').count(),
            'en_proceso': reportes.filter(estado__nombre__in=['En Revisión', 'Asignado', 'En Proceso']).count(),
            'resueltos': reportes.filter(estado__nombre='Resuelto').count(),
        }
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def actualizar_perfil(request):
    """Vista para actualizar datos del perfil"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        user.telefono = request.POST.get('telefono', '')
        user.save()
        
        messages.success(request, '¡Perfil actualizado exitosamente!')
        return redirect('usuarios:perfil')
    
    return redirect('usuarios:perfil')


@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña"""
    if request.method == 'POST':
        from django.contrib.auth import update_session_auth_hash
        
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # SE Verificar contraseña actual
        if not request.user.check_password(old_password):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('usuarios:perfil')
        
        # SE Verificar que las nuevas contraseñas coincidan
        if new_password1 != new_password2:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return redirect('usuarios:perfil')
        
        # SE Validar longitud mínima
        if len(new_password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('usuarios:perfil')
        
        # SE Cambiar contraseña
        request.user.set_password(new_password1)
        request.user.save()
        
        # SE Mantener la sesión activa
        update_session_auth_hash(request, request.user)
        
        messages.success(request, '¡Contraseña cambiada exitosamente!')
        return redirect('usuarios:perfil')
    
    return redirect('usuarios:perfil')


@login_required
def notificaciones_view(request):
    """Vista de notificaciones del usuario"""
    # SE Contar no leídas primero
    no_leidas = Notificacion.objects.filter(
        usuario=request.user,
        leido=False
    ).count()
    
    # SE Obtener últimas 50 notificaciones
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-enviado_en')[:50]
    
    context = {
        'notificaciones': notificaciones,
        'no_leidas': no_leidas
    }
    return render(request, 'usuarios/notificaciones.html', context)


@login_required
def marcar_notificaciones_leidas(request):
    """Marca todas las notificaciones como leídas"""
    Notificacion.objects.filter(
        usuario=request.user,
        leido=False
    ).update(leido=True)
    
    messages.success(request, 'Notificaciones marcadas como leídas.')
    return redirect('usuarios:notificaciones')


# SE ==================================================
# SE VISTAS PARA TÉCNICOS
# SE ==================================================

@login_required
def cambiar_estado_reporte(request, pk):
    """Permite al técnico cambiar el estado de un reporte asignado"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # SE Verificar que el técnico tenga este reporte asignado
    if not Asignacion.objects.filter(reporte=reporte, tecnico=request.user).exists():
        messages.error(request, 'Este reporte no está asignado a ti.')
        return redirect('usuarios:tecnico_home')
    
    if request.method == 'POST':
        nuevo_estado_id = request.POST.get('estado')
        notas = request.POST.get('notas', '')
        
        nuevo_estado = get_object_or_404(EstadoReporte, id=nuevo_estado_id)
        
        # SE Cambiar estado
        estado_anterior = reporte.estado
        reporte.estado = nuevo_estado
        reporte.save()
        
        # SE Registrar en historial
        HistorialReporte.objects.create(
            reporte=reporte,
            usuario=request.user,
            accion='Cambio de estado',
            detalles=f'{estado_anterior.nombre} → {nuevo_estado.nombre}. Notas: {notas}'
        )
        
        # SE Crear notificación para el ciudadano
        Notificacion.objects.create(
            usuario=reporte.usuario,
            reporte=reporte,
            canal='app',
            mensaje=f'Tu reporte "{reporte.titulo}" cambió a estado: {nuevo_estado.nombre}'
        )
        
        messages.success(request, f'Estado actualizado a: {nuevo_estado.nombre}')
        return redirect('usuarios:tecnico_home')
    
    estados = EstadoReporte.objects.all()
    
    return render(request, 'reportes/cambiar_estado.html', {
        'reporte': reporte,
        'estados': estados
    })


@login_required
def subir_evidencia_reparacion(request, pk):
    """Permite al técnico subir evidencia de la reparación"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # SE Verificar asignación
    if not Asignacion.objects.filter(reporte=reporte, tecnico=request.user).exists():
        messages.error(request, 'No tienes permiso para subir evidencias a este reporte.')
        return redirect('usuarios:tecnico_home')
    
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        notas = request.POST.get('notas', '')
        
        if archivo:
            # SE Determinar tipo
            if archivo.content_type.startswith('image'):
                tipo = 'foto'
            elif archivo.content_type.startswith('video'):
                tipo = 'video'
            else:
                tipo = 'documento'
            
            # SE Crear evidencia MARCADA COMO REPARACIÓN
            Evidencia.objects.create(
                reporte=reporte,
                tipo_evidencia=tipo,
                archivo=archivo,
                nombre_archivo=archivo.name,
                tamano_bytes=archivo.size,
                subida_por=request.user,  # Identifica quién subió la evidencia
                es_evidencia_reparacion=True  # Marca que es evidencia de reparación
            )
            
            # SE Registrar en historial
            HistorialReporte.objects.create(
                reporte=reporte,
                usuario=request.user,
                accion='Evidencia de reparación subida',
                detalles=f'Archivo: {archivo.name}. {notas}'
            )
            
            # SE Notificar al ciudadano (opcional)
            Notificacion.objects.create(
                usuario=reporte.usuario,
                reporte=reporte,
                canal='app',
                mensaje=f'Se ha subido evidencia de reparación para tu reporte: {reporte.titulo}'
            )
            
            messages.success(request, 'Evidencia de reparación subida correctamente.')
            return redirect('reportes:cambiar_estado_reporte', pk=reporte.pk)
        else:
            messages.error(request, 'Debes seleccionar un archivo.')
    
    return render(request, 'reportes/subir_evidencia_reparacion.html', {
        'reporte': reporte
    })


# SE ==================================================
# SE VISTAS PARA AUTORIDADES
# SE ==================================================

@login_required
def asignar_tecnico(request, pk):
    """Permite a la autoridad asignar un técnico a un reporte"""
    
    # SE Verificar que sea autoridad o admin
    if request.user.rol.nombre not in ['Autoridad', 'Administrador']:
        messages.error(request, 'No tienes permisos para asignar técnicos.')
        return redirect('usuarios:home')
    
    reporte = get_object_or_404(Reporte, pk=pk)
    
    if request.method == 'POST':
        tecnico_id = request.POST.get('tecnico')
        notas = request.POST.get('notas', '')
        
        tecnico = get_object_or_404(Usuario, id=tecnico_id)
        
        # SE Crear asignación
        asignacion = Asignacion.objects.create(
            reporte=reporte,
            tecnico=tecnico,
            asignado_por=request.user,
            notas=notas
        )
        
        # SE Cambiar estado a "Asignado"
        estado_asignado = EstadoReporte.objects.get(nombre='Asignado')
        reporte.estado = estado_asignado
        reporte.save()
        
        # SE Registrar en historial
        HistorialReporte.objects.create(
            reporte=reporte,
            usuario=request.user,
            accion='Reporte asignado',
            detalles=f'Asignado a técnico: {tecnico.get_full_name() or tecnico.username}'
        )
        
        # SE Notificar al técnico
        Notificacion.objects.create(
            usuario=tecnico,
            reporte=reporte,
            canal='app',
            mensaje=f'Se te ha asignado el reporte: {reporte.titulo} en {reporte.direccion}'
        )
        
        messages.success(request, f'Reporte asignado a {tecnico.username}')
        return redirect('usuarios:autoridad_home')
    
    # SE Obtener solo técnicos
    tecnicos = Usuario.objects.filter(rol__nombre='Técnico', activo=True)
    
    return render(request, 'reportes/asignar_tecnico.html', {
        'reporte': reporte,
        'tecnicos': tecnicos
    })


@login_required
def lista_reportes_autoridad(request):
    """Vista de todos los reportes para autoridades con filtros"""
    
    if request.user.rol.nombre not in ['Autoridad', 'Administrador']:
        messages.error(request, 'No tienes permisos para ver esta página.')
        return redirect('usuarios:home')
    
    # SE Obtener todos los reportes
    reportes = Reporte.objects.all().select_related(
        'usuario', 'estado', 'prioridad'
    ).prefetch_related('asignaciones__tecnico').order_by('-reportado_en')
    
    # SE Filtros
    estado_filtro = request.GET.get('estado')
    prioridad_filtro = request.GET.get('prioridad')
    
    if estado_filtro:
        reportes = reportes.filter(estado__id=estado_filtro)
    
    if prioridad_filtro:
        reportes = reportes.filter(prioridad__id=prioridad_filtro)
    
    # SE Estadísticas
    total_reportes = Reporte.objects.count()
    sin_asignar = Reporte.objects.filter(asignaciones__isnull=True).count()
    en_proceso = Reporte.objects.filter(estado__nombre='En Proceso').count()
    resueltos = Reporte.objects.filter(estado__nombre='Resuelto').count()
    
    estados = EstadoReporte.objects.all()
    prioridades = PrioridadReporte.objects.all()
    
    return render(request, 'reportes/lista_reportes_autoridad.html', {
        'reportes': reportes,
        'estados': estados,
        'prioridades': prioridades,
        'total_reportes': total_reportes,
        'sin_asignar': sin_asignar,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
    })

@login_required
def cambiar_estado_reporte(request, pk):
    """Permite al técnico cambiar el estado de un reporte asignado"""
    reporte = get_object_or_404(Reporte, pk=pk)
    
    # SE Verificar que el técnico tenga este reporte asignado
    if not Asignacion.objects.filter(reporte=reporte, tecnico=request.user).exists():
        messages.error(request, 'Este reporte no está asignado a ti.')
        return redirect('usuarios:tecnico_home')
    
    if request.method == 'POST':
        nuevo_estado_id = request.POST.get('estado')
        comentarios = request.POST.get('comentarios', '').strip()
        tiempo_empleado = request.POST.get('tiempo_empleado', '')
        materiales_usados = request.POST.get('materiales_usados', '')
        evidencia_archivo = request.FILES.get('evidencia')
        
        # VALIDACIONES
        if not comentarios or len(comentarios) < 10:
            messages.error(request, 'Debes agregar comentarios detallados sobre el trabajo realizado (mínimo 10 caracteres).')
            estados = EstadoReporte.objects.all()
            evidencias_previas_count = Evidencia.objects.filter(
                reporte=reporte,
                es_evidencia_reparacion=True,
                subida_por=request.user
            ).count()
            return render(request, 'reportes/cambiar_estado.html', {
                'reporte': reporte,
                'estados': estados,
                'evidencias_previas_count': evidencias_previas_count
            })
        
        # Verificar si hay evidencias previas o nueva
        evidencias_previas = Evidencia.objects.filter(
            reporte=reporte,
            es_evidencia_reparacion=True,
            subida_por=request.user
        ).exists()
        
        if not evidencia_archivo and not evidencias_previas:
            messages.error(request, 'Debes subir al menos una evidencia fotográfica de la reparación.')
            estados = EstadoReporte.objects.all()
            evidencias_previas_count = 0
            return render(request, 'reportes/cambiar_estado.html', {
                'reporte': reporte,
                'estados': estados,
                'evidencias_previas_count': evidencias_previas_count
            })
        
        nuevo_estado = get_object_or_404(EstadoReporte, id=nuevo_estado_id)
        
        # SE Cambiar estado
        estado_anterior = reporte.estado
        reporte.estado = nuevo_estado
        reporte.save()
        
        # SE Subir evidencia si se proporcionó
        if evidencia_archivo:
            # Determinar tipo
            if evidencia_archivo.content_type.startswith('image'):
                tipo = 'foto'
            elif evidencia_archivo.content_type.startswith('video'):
                tipo = 'video'
            else:
                tipo = 'documento'
            
            Evidencia.objects.create(
                reporte=reporte,
                tipo_evidencia=tipo,
                archivo=evidencia_archivo,
                nombre_archivo=evidencia_archivo.name,
                tamano_bytes=evidencia_archivo.size,
                subida_por=request.user,
                es_evidencia_reparacion=True
            )
        
        # SE Construir detalles
        detalles_parts = [f'{estado_anterior.nombre} → {nuevo_estado.nombre}']
        if tiempo_empleado:
            detalles_parts.append(f'Tiempo: {tiempo_empleado}')
        if materiales_usados:
            detalles_parts.append(f'Materiales: {materiales_usados}')
        detalles_parts.append(f'Observaciones: {comentarios}')
        
        detalles = '\n'.join(detalles_parts)
        
        # SE Registrar en historial
        HistorialReporte.objects.create(
            reporte=reporte,
            usuario=request.user,
            accion='Cambio de estado',
            detalles=detalles
        )
        
        # SE Crear notificación para el ciudadano
        Notificacion.objects.create(
            usuario=reporte.usuario,
            reporte=reporte,
            canal='app',
            mensaje=f'Tu reporte "{reporte.titulo}" ha sido marcado como: {nuevo_estado.nombre}'
        )
        
        messages.success(request, f'Reporte actualizado exitosamente a: {nuevo_estado.nombre}')
        return redirect('usuarios:tecnico_home')
    
    estados = EstadoReporte.objects.all()
    
    # Contar evidencias previas del técnico
    evidencias_previas_count = Evidencia.objects.filter(
        reporte=reporte,
        es_evidencia_reparacion=True,
        subida_por=request.user
    ).count()
    
    return render(request, 'reportes/cambiar_estado.html', {
        'reporte': reporte,
        'estados': estados,
        'evidencias_previas_count': evidencias_previas_count
    })

@login_required
def borrar_evidencia_reparacion(request, pk):
    """Permite al técnico borrar sus propias evidencias de reparación"""
    evidencia = get_object_or_404(Evidencia, pk=pk)
    
    # Verificar que sea del técnico actual
    if evidencia.subida_por != request.user:
        messages.error(request, 'No puedes eliminar esta evidencia.')
        return redirect('usuarios:tecnico_home')
    
    # Verificar que sea evidencia de reparación
    if not evidencia.es_evidencia_reparacion:
        messages.error(request, 'Solo puedes eliminar evidencias de reparación.')
        return redirect('usuarios:tecnico_home')
    
    reporte_id = evidencia.reporte.pk
    nombre_archivo = evidencia.nombre_archivo
    
    # Eliminar archivo físico (opcional)
    if evidencia.archivo:
        try:
            evidencia.archivo.delete()
        except:
            pass
    
    # Eliminar registro
    evidencia.delete()
    
    # Registrar en historial
    HistorialReporte.objects.create(
        reporte_id=reporte_id,
        usuario=request.user,
        accion='Evidencia de reparación eliminada',
        detalles=f'Archivo eliminado: {nombre_archivo}'
    )
    
    messages.success(request, 'Evidencia eliminada correctamente.')
    return redirect('reportes:cambiar_estado_reporte', pk=reporte_id)

