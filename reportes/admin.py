from django.contrib import admin
from .models import Reporte

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo', 'direccion', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('usuario__username', 'descripcion', 'direccion')
    readonly_fields = ('fecha',)
