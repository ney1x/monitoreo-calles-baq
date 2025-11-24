from django.core.management.base import BaseCommand
from apps.reportes.models import Reporte
from apps.reportes.duplicate_detector import DetectorDuplicados


class Command(BaseCommand):
    help = 'Detecta y marca reportes duplicados existentes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--radio',
            type=float,
            default=0.05,
            help='Radio de búsqueda en kilómetros (default: 0.05 = 50 metros)'
        )
        
        parser.add_argument(
            '--dias',
            type=int,
            default=7,
            help='Ventana temporal en días (default: 7)'
        )
    
    def handle(self, *args, **options):
        from apps.reportes.models import Reporte
        
        radio = options['radio']
        dias = options['dias']
        
        # Actualizar configuración temporal
        DetectorDuplicados.RADIO_BUSQUEDA_KM = radio
        DetectorDuplicados.VENTANA_TEMPORAL_DIAS = dias
        
        self.stdout.write(f'Buscando duplicados con radio de {radio*1000}m y ventana de {dias} días...')
        
        # Obtener reportes con coordenadas que no estén marcados
        reportes = Reporte.objects.filter(
            latitud__isnull=False,
            longitud__isnull=False,
            duplicado=False
        ).order_by('reportado_en')
        
        total = reportes.count()
        procesados = 0
        duplicados_encontrados = 0
        
        for reporte in reportes:
            es_duplicado, grupo = DetectorDuplicados.detectar_y_marcar_duplicado(reporte)
            procesados += 1
            
            if es_duplicado:
                duplicados_encontrados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[{procesados}/{total}] Reporte #{reporte.id} marcado como duplicado (Grupo #{grupo.id})'
                    )
                )
            else:
                self.stdout.write(f'[{procesados}/{total}] Reporte #{reporte.id} - único')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado: {duplicados_encontrados} duplicados encontrados de {total} reportes'
            )
        )