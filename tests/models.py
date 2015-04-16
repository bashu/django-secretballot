from django.db import models
import secretballot

class Link(models.Model):
    url = models.URLField()

secretballot.enable_voting_on(Link)
