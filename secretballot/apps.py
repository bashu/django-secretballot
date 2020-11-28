from django.apps import AppConfig as DefaultAppConfig


class AppConfig(DefaultAppConfig):

    name = "secretballot"

    def ready(self):
        # Ensure everything below is only ever run once
        if getattr(AppConfig, "has_run_ready", False):
            return
        AppConfig.has_run_ready = True

        try:
            from . import receivers  # noqa F401
        except ImportError:
            pass
