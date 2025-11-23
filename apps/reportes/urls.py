from django.urls import path
from . import views
from apps.usuarios import views as usuarios_views

app_name = 'reportes'

urlpatterns = [
    # SE Públicas
    path('', views.lista_reportes, name='lista_reportes'),
    path('mapa/', views.mapa_reportes, name='mapa'),
    
    # SE Ciudadanos
    path('crear/', views.crear_reporte, name='crear_reporte'),
    path('exitoso/<int:pk>/', views.reporte_exitoso, name='reporte_exitoso'),
    path('detalle/<int:pk>/', views.detalle_reporte, name='detalle_reporte'),
    path('agregar-evidencia/<int:pk>/', views.agregar_evidencia, name='agregar_evidencia'),
    
    # SE Técnicos
    path('cambiar-estado/<int:pk>/', usuarios_views.cambiar_estado_reporte, name='cambiar_estado_reporte'),
    path('subir-evidencia-reparacion/<int:pk>/', usuarios_views.subir_evidencia_reparacion, name='subir_evidencia_reparacion'),
    
    # SE Autoridades
    path('asignar-tecnico/<int:pk>/', usuarios_views.asignar_tecnico, name='asignar_tecnico'),
    path('lista-autoridad/', usuarios_views.lista_reportes_autoridad, name='lista_reportes_autoridad'),

    # Crear reporte desde mapa
    path('crear-desde-mapa/', views.crear_reporte_desde_mapa, name='crear_reporte_desde_mapa'),

]
