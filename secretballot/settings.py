from django.conf import settings

MODEL_VOTE = getattr(settings, "SECRETBALLOT_VOTE_MODEL", "secretballot.Vote")
