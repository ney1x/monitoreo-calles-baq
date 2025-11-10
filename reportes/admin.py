from django.contrib import admin
from .models import (
    Reporte,
    PrioridadReporte,
    EstadoReporte,
    GrupoDuplicado,
    Evidencia
)


# -----------------------------
# ADMIN DE REPORTES
# -----------------------------
@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'usuario',
        'tipo',
        'prioridad',
        'estado',
        'duplicado',
        'direccion',
        'fecha',
        'fechaActualizacion',
    )

    list_filter = (
        'tipo',
        'prioridad',
        'estado',
        'duplicado',
        'fecha',
    )

    search_fields = (
        'titulo',
        'descripcion',
        'direccion',
        'usuario__username',
    )

    readonly_fields = (
        'fecha',
        'fechaActualizacion',
    )

    # Mejor orden en el formulario
    fieldsets = (
        ('Información general', {
            'fields': ('titulo', 'tipo', 'descripcion', 'usuario')
        }),
        ('Ubicación', {
            'fields': ('direccion',)
        }),
        ('Estado del reporte', {
            'fields': ('prioridad', 'estado', 'duplicado', 'grupoDuplicado')
        }),
        ('Archivos adjuntos', {
            'fields': ('foto', 'video')
        }),
        ('Fechas', {
            'fields': ('fecha', 'fechaActualizacion')
        }),
    )


# -----------------------------
# ADMIN DE PRIORIDAD
# -----------------------------
@admin.register(PrioridadReporte)
class PrioridadReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


# -----------------------------
# ADMIN DE ESTADO
# -----------------------------
@admin.register(EstadoReporte)
class EstadoReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


# -----------------------------
# ADMIN DE GRUPO DUPLICADO
# -----------------------------
@admin.register(GrupoDuplicado)
class GrupoDuplicadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fechaDeteccion', 'razon')
    search_fields = ('razon',)
    readonly_fields = ('fechaDeteccion',)


# -----------------------------
# ADMIN DE EVIDENCIA
# -----------------------------
@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte', 'archivo', 'fechaSubida')
    readonly_fields = ('fechaSubida',)
    search_fields = ('reporte__titulo', 'reporte__usuario__username')
