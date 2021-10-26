from etc.toolbox import get_model_class_from_settings

from secretballot import settings


def get_vote_model():
    return get_model_class_from_settings(settings, "MODEL_VOTE")
