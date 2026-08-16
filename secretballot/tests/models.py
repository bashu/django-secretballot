from django.db import models


class Link(models.Model):
    url = models.URLField()

    def __str__(self):
        return self.url


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

    def __str__(self):
        return self.url


# Used for testing custom manager_name
class NonAutomaticEnabledModel(models.Model):
    url = models.URLField()

    def __str__(self):
        return self.url
