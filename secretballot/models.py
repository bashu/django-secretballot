from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

VOTE_CHOICES = (
    (+1, "+1"),
    (-1, "-1"),
)


class VoteBase(models.Model):
    token = models.CharField(max_length=50)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    # generic foreign key to the model being voted upon
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True, null=True)

    class Meta:
        abstract = True
        unique_together = (("token", "content_type", "object_id"),)

    def __str__(self):
        return "{} from {} on {}".format(self.get_vote_display(), self.token, self.content_object)


class Vote(VoteBase):
    class Meta(VoteBase.Meta):
        db_table = "secretballot_vote"
