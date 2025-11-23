from django.contrib import admin
from .models import (
    PrioridadReporte,
    EstadoReporte,
    GrupoDuplicado,
    Reporte,
    Evidencia,
    Asignacion,
    HistorialReporte,
    Notificacion,
    RegistroAuditoria
)


# ============================================
# CATÁLOGOS
# ============================================

@admin.register(PrioridadReporte)
class PrioridadReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'nivel_gravedad')
    list_editable = ('nivel_gravedad',)
    ordering = ('nivel_gravedad',)


@admin.register(EstadoReporte)
class EstadoReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(GrupoDuplicado)
class GrupoDuplicadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fechaDeteccion', 'razon')
    readonly_fields = ('fechaDeteccion',)


# ============================================
# REPORTE CON INLINES
# ============================================

class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    readonly_fields = ('fechaSubida', 'tamano_bytes')


class AsignacionInline(admin.TabularInline):
    model = Asignacion
    extra = 0
    readonly_fields = ('fecha_asignacion',)


class HistorialInline(admin.TabularInline):
    model = HistorialReporte
    extra = 0
    readonly_fields = ('usuario', 'accion', 'detalles', 'fecha_accion')
    can_delete = False


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'tipo',
        'usuario',
        'get_estado',
        'get_prioridad',
        'duplicado',
        'reportado_en',
    )

    list_filter = ('tipo', 'estado', 'prioridad', 'duplicado', 'reportado_en')
    search_fields = ('titulo', 'descripcion', 'direccion', 'usuario__username')
    readonly_fields = ('reportado_en', 'actualizado_en')

    fieldsets = (
        ('Información General', {
            'fields': ('titulo', 'tipo', 'descripcion', 'usuario')
        }),
        ('Georreferenciación', {
            'fields': ('latitud', 'longitud', 'direccion')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad', 'duplicado', 'grupoDuplicado')
        }),
        ('Fechas', {
            'fields': ('reportado_en', 'actualizado_en')
        }),
    )

    inlines = [EvidenciaInline, AsignacionInline, HistorialInline]

    def get_estado(self, obj):
        return obj.estado.nombre if obj.estado else '-'
    get_estado.short_description = 'Estado'

    def get_prioridad(self, obj):
        return obj.prioridad.nombre if obj.prioridad else '-'
    get_prioridad.short_description = 'Prioridad'


# ============================================
# OTROS MODELOS
# ============================================

@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte', 'tipo_evidencia', 'nombre_archivo', 'es_evidencia_reparacion', 'subida_por', 'fechaSubida')
    list_filter = ('tipo_evidencia', 'es_evidencia_reparacion', 'fechaSubida')
    readonly_fields = ('fechaSubida', 'tamano_bytes')

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte', 'tecnico', 'asignado_por', 'fecha_asignacion')
    list_filter = ('fecha_asignacion',)
    readonly_fields = ('fecha_asignacion',)


@admin.register(HistorialReporte)
class HistorialReporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporte', 'usuario', 'accion', 'fecha_accion')
    list_filter = ('fecha_accion',)
    readonly_fields = ('fecha_accion',)

    def has_add_permission(self, request):
        return False  # Se crean automáticamente

    def has_delete_permission(self, request, obj=None):
        return False  # No se permite eliminar auditoría


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'canal', 'mensaje_corto', 'leido', 'enviado_en')
    list_filter = ('canal', 'leido', 'enviado_en')
    readonly_fields = ('enviado_en',)

    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento', 'usuario', 'fecha_evento')
    list_filter = ('evento', 'fecha_evento')
    readonly_fields = ('fecha_evento',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
