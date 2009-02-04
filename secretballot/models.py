from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

VOTE_TABLE = 'secretballot_vote'
VOTE_CHOICES = (
    (+1, '+1'),
    (-1, '-1'),
)

class Vote(models.Model):
    token = models.CharField(max_length=50)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    # generic foreign key to a VotableModel
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('token', 'content_type', 'object_id'),)

    def __unicode__(self):
        return '%s from %s on %s' % (self.get_vote_display(), self.token,
                                     self.content_object)
