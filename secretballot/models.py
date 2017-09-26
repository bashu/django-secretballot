from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.encoding import python_2_unicode_compatible

VOTE_CHOICES = (
    (+1, '+1'),
    (-1, '-1'),
)


@python_2_unicode_compatible
class Vote(models.Model):
    token = models.CharField(max_length=50)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    # generic foreign key to the model being voted upon
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True, null=True)

    class Meta:
        unique_together = (('token', 'content_type', 'object_id'),)

    def __str__(self):
        return '{} from {} on {}'.format(self.get_vote_display(), self.token, self.content_object)
