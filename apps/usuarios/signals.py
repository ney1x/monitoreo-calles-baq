from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone


@receiver(user_logged_in)
def actualizar_ultimo_inicio(sender, request, user, **kwargs):
    """Actualizar ultimoInicioSesion al hacer login"""
    user.ultimoInicioSesion = timezone.now()
    user.save(update_fields=['ultimoInicioSesion'])
