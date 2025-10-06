from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_reporte, name='crear_reporte'),
    path('exitoso/', views.reporte_exitoso, name='reporte_exitoso'),
    path('mis_reportes/', views.mis_reportes, name='mis_reportes'),
]
