from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil y notificaciones
    path('perfil/', views.perfil_view, name='perfil'),
    path('notificaciones/', views.notificaciones_view, name='notificaciones'),

    # Rutas por rol
    path('ciudadano/', views.ciudadano_home, name='ciudadano_home'),
    path('tecnico/', views.tecnico_home, name='tecnico_home'),
    path('autoridad/', views.autoridad_home, name='autoridad_home'),
]
