from django.apps import AppConfig


class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reportes'

    def ready(self):
        import apps.reportes.duplicate_detector
        from . import duplicate_detector
        from . import signals
