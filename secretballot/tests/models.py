from django.db import models

import secretballot


class Link(models.Model):
    url = models.URLField()


# used for testing field renames
class WeirdLink(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


# TODO?: base_manager?


# Used for testing custom manager_name
class AnotherLink(models.Model):
    url = models.URLField()


# Used for testing custom manager_name
class NonAutomaticEnabledModel(models.Model):
    url = models.URLField()
