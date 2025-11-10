from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .forms import RegistroForm, LoginForm
from .models import Usuario
from apps.reportes.models import Reporte, Notificacion

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

                # REGISTRA LA FECHA DE INICIO DE SESIÓN
                user.registrar_inicio_sesion()

                messages.success(request, f"Bienvenido, {username}.")

                # REDIRECCIÓN CORRECTA SEGÚN ROLES DEL MODELO
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
                
                # Si es staff sin rol específico
                if user.is_staff:
                    return redirect('/admin/')
                
                # Fallback a ciudadano
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
    # Si está autenticado Y tiene un parámetro especial, mostrar landing de todos modos
    if request.GET.get('public'):
        reportes_count = Reporte.objects.count()
        return render(request, 'home.html', {
            'reportes_count': reportes_count,
            'show_public': True
        })
    
    if request.user.is_authenticated:
        # Redirigir según rol
        if request.user.rol:
            rol_nombre = request.user.rol.nombre
            if rol_nombre == 'Ciudadano':
                return redirect('usuarios:ciudadano_home')
            elif rol_nombre == 'Técnico':
                return redirect('usuarios:tecnico_home')
            elif rol_nombre == 'Autoridad':
                return redirect('usuarios:autoridad_home')
            elif rol_nombre == 'Administrador':
                return redirect('usuarios:autoridad_home')  # Admin ve dashboard de autoridad
        
        # Si es staff sin rol, ir a admin
        if request.user.is_staff:
            return redirect('usuarios:autoridad_home')  # Dashboard en lugar de /admin/
        
        # Fallback a ciudadano
        return redirect('usuarios:ciudadano_home')
    
    # Mostrar landing page para usuarios no autenticados
    reportes_count = Reporte.objects.count()
    return render(request, 'home.html', {
        'reportes_count': reportes_count
    })


# Vistas por rol
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
    # Reportes asignados a este técnico
    mis_asignaciones = Reporte.objects.filter(
        asignaciones__tecnico=request.user
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
    
    # Estadísticas generales
    estadisticas = {
        'total': Reporte.objects.count(),
        'nuevos': Reporte.objects.filter(estado__nombre='Nuevo').count(),
        'en_proceso': Reporte.objects.filter(
            estado__nombre__in=['En Revisión', 'Asignado', 'En Proceso']
        ).count(),
        'resueltos': Reporte.objects.filter(estado__nombre='Resuelto').count(),
        'criticos': Reporte.objects.filter(prioridad__nombre='Crítica').count(),
    }
    
    # Reportes recientes críticos
    reportes_criticos = Reporte.objects.filter(
        prioridad__nombre='Crítica'
    ).exclude(
        estado__nombre='Resuelto'
    ).order_by('-reportado_en')[:5]
    
    # Reportes por prioridad
    por_prioridad = Reporte.objects.values('prioridad__nombre').annotate(
        count=Count('id')
    ).order_by('prioridad__nivel_gravedad')
    
    # Reportes por estado
    por_estado = Reporte.objects.values('estado__nombre').annotate(
        count=Count('id')
    )
    
    context = {
        'estadisticas': estadisticas,
        'reportes_criticos': reportes_criticos,
        'por_prioridad': por_prioridad,
        'por_estado': por_estado,
    }
    return render(request, 'usuarios/autoridad_home.html', context)


@login_required
def perfil_view(request):
    """Vista del perfil del usuario"""
    return render(request, 'usuarios/perfil.html')


@login_required
def notificaciones_view(request):
    """Vista de notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-enviado_en')[:20]
    
    # Marcar como leídas al visualizar
    Notificacion.objects.filter(
        usuario=request.user,
        leido=False
    ).update(leido=True)
    
    context = {
        'notificaciones': notificaciones
    }
    return render(request, 'usuarios/notificaciones.html', context)