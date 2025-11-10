from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reporte, HistorialReporte


@receiver(post_save, sender=Reporte)
def crear_historial_inicial(sender, instance, created, **kwargs):
    """Crear entrada en historial cuando se crea un reporte"""
    if created:
        HistorialReporte.objects.create(
            reporte=instance,
            usuario=instance.usuario,
            accion="Reporte creado",
            detalles=f"Reporte '{instance.titulo}' creado en {instance.direccion}"
        )
