"""
Sistema de Detección de Reportes Duplicados
Agrupa reportes cercanos geográficamente del mismo tipo
"""

from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
from datetime import timedelta
from django.utils import timezone
from django.db import transaction


class DetectorDuplicados:
    """
    Detecta y agrupa reportes duplicados basándose en:
    - Proximidad geográfica (radio configurable)
    - Tipo de falla similar
    - Ventana temporal
    """

    # Radio de búsqueda en kilómetros (50 metros = 0.05 km)
    RADIO_BUSQUEDA_KM = 0.05

    # Ventana temporal en días
    VENTANA_TEMPORAL_DIAS = 7

    @staticmethod
    def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
        """ Calcula distancia usando Haversine """
        R = 6371.0

        lat1_rad = radians(float(lat1))
        lon1_rad = radians(float(lon1))
        lat2_rad = radians(float(lat2))
        lon2_rad = radians(float(lon2))

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    @classmethod
    def buscar_reportes_cercanos(cls, reporte, radio_km=None):
        from apps.reportes.models import Reporte

        if not reporte.latitud or not reporte.longitud:
            return Reporte.objects.none()

        # Convertir a Decimal por si vienen como string
        lat = Decimal(str(reporte.latitud))
        lon = Decimal(str(reporte.longitud))

        radio = radio_km or cls.RADIO_BUSQUEDA_KM

        # 1 grado ≈ 111 km
        delta_lat = Decimal(radio / 111.0)
        delta_lon = Decimal(radio / (111.0 * cos(radians(float(lat)))))

        lat_min = lat - delta_lat
        lat_max = lat + delta_lat
        lon_min = lon - delta_lon
        lon_max = lon + delta_lon

        fecha_min = reporte.reportado_en - timedelta(days=cls.VENTANA_TEMPORAL_DIAS)
        fecha_max = reporte.reportado_en + timedelta(days=cls.VENTANA_TEMPORAL_DIAS)

        candidatos = Reporte.objects.filter(
            latitud__gte=lat_min,
            latitud__lte=lat_max,
            longitud__gte=lon_min,
            longitud__lte=lon_max,
            tipo=reporte.tipo,
            reportado_en__gte=fecha_min,
            reportado_en__lte=fecha_max
        ).exclude(id=reporte.id)

        # Filtrar por distancia exacta
        reportes_cercanos = []
        for candidato in candidatos:
            distancia = cls.calcular_distancia_haversine(
                lat, lon,
                Decimal(str(candidato.latitud)),
                Decimal(str(candidato.longitud))
            )
            if distancia <= radio:
                reportes_cercanos.append(candidato.id)

        return Reporte.objects.filter(id__in=reportes_cercanos)

    @classmethod
    @transaction.atomic
    def detectar_y_marcar_duplicado(cls, reporte):
        from apps.reportes.models import GrupoDuplicado, HistorialReporte

        reportes_cercanos = cls.buscar_reportes_cercanos(reporte)

        if not reportes_cercanos.exists():
            return False, None

        # Verificar si alguno ya tiene grupo
        grupos_existentes = GrupoDuplicado.objects.filter(
            reportes__in=reportes_cercanos
        ).distinct()

        if grupos_existentes.exists():
            grupo = grupos_existentes.first()
            reporte.duplicado = True
            reporte.grupoDuplicado = grupo
            reporte.save()

            HistorialReporte.objects.create(
                reporte=reporte,
                usuario=None,
                accion='Marcado como duplicado',
                detalles=f'Agrupado con {grupo.reportes.count()} reportes similares en {cls.RADIO_BUSQUEDA_KM * 1000}m'
            )

            return True, grupo

        else:
            # Crear grupo nuevo
            grupo = GrupoDuplicado.objects.create(
                razon=f'Reportes de tipo "{reporte.get_tipo_display()}" en un radio de {cls.RADIO_BUSQUEDA_KM * 1000}m'
            )

            reportes_para_agrupar = list(reportes_cercanos) + [reporte]

            for rep in reportes_para_agrupar:
                rep.duplicado = True
                rep.grupoDuplicado = grupo
                rep.save()

                HistorialReporte.objects.create(
                    reporte=rep,
                    usuario=None,
                    accion='Marcado como duplicado',
                    detalles=f'Agrupado con otros {len(reportes_para_agrupar)-1} reportes similares'
                )

            return True, grupo

    @classmethod
    def obtener_reporte_principal(cls, grupo):
        return grupo.reportes.order_by('reportado_en').first()

    @classmethod
    def obtener_estadisticas_grupo(cls, grupo):
        reportes = grupo.reportes.all()
        principal = cls.obtener_reporte_principal(grupo)

        return {
            'total_reportes': reportes.count(),
            'reporte_principal': principal,
            'fecha_primer_reporte': principal.reportado_en if principal else None,
            'fecha_ultimo_reporte': reportes.order_by('-reportado_en').first().reportado_en,
            'usuarios_reportaron': reportes.values('usuario').distinct().count(),
            'tiene_evidencias': reportes.filter(evidencias__isnull=False).exists(),
            'total_evidencias': sum(r.evidencias.count() for r in reportes),
        }


# ============================================
# SIGNALS PARA DETECCIÓN AUTOMÁTICA
# ============================================

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.reportes.models import Reporte


@receiver(post_save, sender=Reporte)
def detectar_duplicados_automaticamente(sender, instance, created, **kwargs):
    """ Detecta duplicados al crear un reporte """
    if created and instance.latitud and instance.longitud:
        DetectorDuplicados.detectar_y_marcar_duplicado(instance)
