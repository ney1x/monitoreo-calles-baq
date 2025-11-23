from django.db import models
from django.conf import settings


# ============================================
# CATÁLOGOS
# ============================================

class PrioridadReporte(models.Model):
    """Catálogo: Baja, Media, Alta, Crítica"""
    nombre = models.CharField(max_length=50, unique=True)
    nivel_gravedad = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Prioridad de Reporte"
        verbose_name_plural = "Prioridades de Reporte"
        ordering = ['nivel_gravedad']

    def __str__(self):
        return self.nombre


class EstadoReporte(models.Model):
    """Catálogo: Nuevo, En Revisión, Asignado, En Proceso, Resuelto, Rechazado"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Estado de Reporte"
        verbose_name_plural = "Estados de Reporte"

    def __str__(self):
        return self.nombre


class GrupoDuplicado(models.Model):
    """Agrupa reportes duplicados"""
    fechaDeteccion = models.DateTimeField(auto_now_add=True)
    razon = models.TextField()

    class Meta:
        verbose_name = "Grupo Duplicado"
        verbose_name_plural = "Grupos Duplicados"

    def __str__(self):
        return f"Grupo #{self.id}"


# ============================================
# REPORTE PRINCIPAL
# ============================================

class Reporte(models.Model):
    """
    Reporte de incidencia vial.
    Según diagrama: id, usuario_id, titulo, descripcion, latitud, longitud, 
    direccion, prioridad_id, estado_id, duplicado, grupo_duplicado_id, 
    reportado_en, actualizado_en
    """
    
    TIPOS_FALLA = (
        ('bache', 'Bache o hueco'),
        ('fisura', 'Fisura o grieta'),
        ('hundimiento', 'Hundimiento de vía'),
        ('desprendimiento', 'Desprendimiento de capa asfáltica'),
        ('inundacion', 'Inundación o encharcamiento'),
        ('obstruccion', 'Obstrucción en la calzada'),
        ('otro', 'Otro'),
    )

    # Relaciones
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reportes'
    )
    prioridad = models.ForeignKey(
        PrioridadReporte,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    estado = models.ForeignKey(
        EstadoReporte,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    grupoDuplicado = models.ForeignKey(
        GrupoDuplicado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes'
    )

    # Campos básicos
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=30, choices=TIPOS_FALLA)
    descripcion = models.TextField()

    # Georreferenciación (OPCIONALES hasta implementar GPS/mapa)
    latitud = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        help_text="Latitud GPS",
        null=True,
        blank=True
    )
    longitud = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        help_text="Longitud GPS",
        null=True,
        blank=True
    )
    direccion = models.CharField(max_length=255, blank=True)

    # Control de duplicados
    duplicado = models.BooleanField(default=False)

    # Timestamps
    reportado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-reportado_en']
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['latitud', 'longitud']),
        ]

    def __str__(self):
        return f"#{self.id} - {self.titulo}"

    def crear(self):
        """Método del diagrama de clases"""
        self.save()
        # Crear entrada en historial
        HistorialReporte.objects.create(
            reporte=self,
            usuario=self.usuario,
            accion="Reporte creado",
            detalles=f"Reporte creado por {self.usuario.username}"
        )
        return self

    def cambiar_estado(self, nuevo_estado, por_usuario):
        """Método del diagrama de clases"""
        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.save()
        
        HistorialReporte.objects.create(
            reporte=self,
            usuario=por_usuario,
            accion=f"Cambio de estado",
            detalles=f"{estado_anterior} → {nuevo_estado}"
        )
        return True


# ============================================
# EVIDENCIAS
# ============================================

class Evidencia(models.Model):
    """
    Evidencias multimedia de un reporte.
    """
    
    TIPO_EVIDENCIA = (
        ('foto', 'Fotografía'),
        ('video', 'Video'),
        ('documento', 'Documento'),
    )

    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='evidencias'
    )
    
    tipo_evidencia = models.CharField(max_length=20, choices=TIPO_EVIDENCIA)
    archivo = models.FileField(upload_to='evidencias/%Y/%m/%d/')
    url_almacenamiento = models.URLField(max_length=500, blank=True)
    nombre_archivo = models.CharField(max_length=255)
    tamano_bytes = models.BigIntegerField(default=0)
    
    # AGREGAR ESTOS CAMPOS
    subida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidencias_subidas'
    )
    es_evidencia_reparacion = models.BooleanField(default=False)
    
    fechaSubida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidencia"
        verbose_name_plural = "Evidencias"

    def __str__(self):
        tipo = "Reparación" if self.es_evidencia_reparacion else "Ciudadano"
        return f"{self.tipo_evidencia} ({tipo}) - Reporte #{self.reporte.id}"

    def save(self, *args, **kwargs):
        # Calcular tamaño automáticamente
        if self.archivo and hasattr(self.archivo, 'size'):
            self.tamano_bytes = self.archivo.size
            if not self.nombre_archivo:
                self.nombre_archivo = self.archivo.name
        super().save(*args, **kwargs)


# ============================================
# ASIGNACIONES
# ============================================

class Asignacion(models.Model):
    """
    Asignación de técnico a reporte.
    Según diagrama: id, reporte_id, tecnico_id, asignado_por, 
    fecha_asignacion, notas
    """
    
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones_tecnico'
    )
    asignado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='asignaciones_creadas'
    )
    
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"

    def __str__(self):
        return f"Reporte #{self.reporte.id} → {self.tecnico.username}"


# ============================================
# HISTORIAL
# ============================================

class HistorialReporte(models.Model):
    """
    Historial de cambios de un reporte.
    Según diagrama: id, reporte_id, usuario_id, accion, detalles, fecha_accion
    """
    
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    accion = models.CharField(max_length=255)
    detalles = models.TextField()
    fecha_accion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historial de Reporte"
        verbose_name_plural = "Historial de Reportes"
        ordering = ['-fecha_accion']

    def __str__(self):
        return f"{self.accion} - {self.fecha_accion.strftime('%d/%m/%Y %H:%M')}"


# ============================================
# NOTIFICACIONES
# ============================================

class Notificacion(models.Model):
    """
    Notificaciones a usuarios.
    Según diagrama: id, usuario_id, reporte_id, canal, mensaje, leido, enviado_en
    """
    
    CANALES = (
        ('email', 'Correo Electrónico'),
        ('sms', 'SMS'),
        ('push', 'Notificación Push'),
        ('app', 'In-App'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    reporte = models.ForeignKey(
        Reporte,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones'
    )
    
    canal = models.CharField(max_length=20, choices=CANALES)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    
    enviado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-enviado_en']

    def __str__(self):
        return f"{self.canal} → {self.usuario.username}"


# ============================================
# AUDITORÍA
# ============================================

class RegistroAuditoria(models.Model):
    """
    Registro general de auditoría del sistema.
    Según diagrama: id, usuario_id, evento, metadatos, fecha_evento
    """
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    evento = models.CharField(max_length=100)
    metadatos = models.JSONField(default=dict, blank=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"{self.evento} - {self.fecha_evento.strftime('%d/%m/%Y')}"