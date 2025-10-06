from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = [
        ('CIUDADANO', 'Ciudadano'),
        ('TECNICO', 'Técnico'),
        ('AUTORIDAD', 'Autoridad'),
        ('ADMIN', 'Administrador'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='CIUDADANO')

    def __str__(self):
        return f"{self.username} ({self.rol})"
