from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()

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
    descripcion = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='reportes/fotos/', blank=True, null=True)
    video = models.FileField(upload_to='reportes/videos/', blank=True, null=True)
    direccion = models.CharField(max_length=255, help_text="Ejemplo: Calle 72 #43-85")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario.username}"
