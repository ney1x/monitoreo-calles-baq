from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()
class PrioridadReporte(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class EstadoReporte(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class GrupoDuplicado(models.Model):
    fechaDeteccion = models.DateTimeField(auto_now_add=True)
    razon = models.TextField()

    def __str__(self):
        return f"Grupo duplicado #{self.id}"


class Evidencia(models.Model):
    reporte = models.ForeignKey('Reporte', on_delete=models.CASCADE, related_name='evidencias')
    archivo = models.FileField(upload_to='evidencias/', null=True, blank=True)
    fechaSubida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia {self.id} del reporte {self.reporte.id}"


class Reporte(models.Model):
    TIPOS = (
        ('bache', 'Bache o hueco'),
        ('fisura', 'Fisura o grieta'),
        ('hundimiento', 'Hundimiento de vía'),
        ('desprendimiento', 'Desprendimiento de capa asfáltica'),
        ('inundacion', 'Inundación o encharcamiento'),
        ('obstruccion', 'Obstrucción en la calzada'),
        ('otro', 'Otro'),
    )

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30, choices=TIPOS)

    # NUEVOS CAMPOS DEL ER/UML
    titulo = models.CharField(max_length=100)
    prioridad = models.ForeignKey(PrioridadReporte, on_delete=models.PROTECT, null=True)
    estado = models.ForeignKey(EstadoReporte, on_delete=models.PROTECT, null=True)
    duplicado = models.BooleanField(default=False)
    grupoDuplicado = models.ForeignKey(GrupoDuplicado, on_delete=models.SET_NULL, null=True, blank=True)

    # CAMPOS ORIGINALES (NO SE TOCAN)
    descripcion = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='reportes/fotos/', blank=True, null=True)
    video = models.FileField(upload_to='reportes/videos/', blank=True, null=True)
    direccion = models.CharField(max_length=255, help_text="Ejemplo: Calle 72 #43-85")

    fecha = models.DateTimeField(auto_now_add=True)
    fechaActualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
