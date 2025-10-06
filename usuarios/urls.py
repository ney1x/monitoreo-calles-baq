from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Rutas por rol
    path('ciudadano/', views.ciudadano_home, name='ciudadano_home'),
    path('tecnico/', views.tecnico_home, name='tecnico_home'),
    path('autoridad/', views.autoridad_home, name='autoridad_home'),
]
