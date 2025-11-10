from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Usuario(AbstractUser):
    ROLES = [
        ('CIUDADANO', 'Ciudadano'),
        ('TECNICO', 'Técnico'),
        ('AUTORIDAD', 'Autoridad'),
        ('ADMIN', 'Administrador'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='CIUDADANO')

    activo = models.BooleanField(default=True)  # campo propio del UML
    creadoEn = models.DateTimeField(auto_now_add=True)
    ultimoInicioSesion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    def registrar_inicio_sesion(self):
        self.ultimoInicioSesion = timezone.now()
        self.save(update_fields=["ultimoInicioSesion"])
