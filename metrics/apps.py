from django.apps import AppConfig


class MetricsConfig(AppConfig):
    name = "metrics"
    verbose_name = "Métricas"

    def ready(self):
        from . import signals  # noqa: F401
