from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.lista_reportes, name='lista_reportes'),
    path('crear/', views.crear_reporte, name='crear_reporte'),
    path('exitoso/<int:pk>/', views.reporte_exitoso, name='reporte_exitoso'),
    path('mis-reportes/', views.mis_reportes, name='mis_reportes'),
    path('detalle/<int:pk>/', views.detalle_reporte, name='detalle_reporte'),
    path('agregar-evidencia/<int:pk>/', views.agregar_evidencia, name='agregar_evidencia'),
    path('mapa/', views.mapa_reportes, name='mapa'),
]
