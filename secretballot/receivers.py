from django.apps import apps
from django.conf import settings

from . import enable_voting_on

for model_path, attrs in getattr(settings, "SECRETBALLOT_FOR_MODELS", {}).items():
    app_label, model_name = model_path.split(".")

    enable_voting_on(apps.get_model(app_label, model_name), **attrs)
