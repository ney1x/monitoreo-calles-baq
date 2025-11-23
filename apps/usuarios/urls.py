from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    
    # SE Perfil y configuración
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
    path('perfil/cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),
    path('notificaciones/marcar-leidas/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),

    # SE Rutas por rol (Dashboards)
    path('ciudadano/', views.ciudadano_home, name='ciudadano_home'),
    path('tecnico/', views.tecnico_home, name='tecnico_home'),
    path('autoridad/', views.autoridad_home, name='autoridad_home'),
    
    # SE Borrar evidencia de reparación (AGREGAR ESTA LÍNEA)
    path('evidencia/borrar/<int:pk>/', views.borrar_evidencia_reparacion, name='borrar_evidencia_reparacion'),
]
