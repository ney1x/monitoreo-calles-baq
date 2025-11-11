from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Rol(models.Model):
    """Catálogo de roles del sistema"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    """
    Usuario extendido del sistema.
    Cumple con el diagrama: id, nombre, correo, contrasenaHash, telefono, rol, activo, creadoEn, ultimoInicioSesion
    """
    # SE AbstractUser ya trae: username, email, password, first_name, last_name
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='usuarios',
        null=True,
        blank=True
    )
    
    activo = models.BooleanField(default=True)
    creadoEn = models.DateTimeField(auto_now_add=True)
    ultimoInicioSesion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        rol_nombre = self.rol.nombre if self.rol else 'Sin rol'
        return f"{self.username} ({rol_nombre})"

    def registrar_inicio_sesion(self):
        """Método del diagrama de clases"""
        self.ultimoInicioSesion = timezone.now()
        self.save(update_fields=['ultimoInicioSesion'])
