from django.db import models
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

class VotableManager(models.Manager):

    def get_query_set(self):
        db_table = self.model._meta.db_table
        pk_name = self.model._meta.pk.attname
        content_type = ContentType.objects.get_for_model(self.model).id
        downvote_query = '(SELECT COUNT(*) from %s WHERE vote=-1 AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
        upvote_query = '(SELECT COUNT(*) from %s WHERE vote=1 AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
        return super(VotableManager, self).get_query_set().extra(
            select={'total_upvotes': upvote_query, 'total_downvotes': downvote_query})

    def from_token(self, token):
        db_table = self.model._meta.db_table
        pk_name = self.model._meta.pk.attname
        content_type = ContentType.objects.get_for_model(self.model).id
        query = '(SELECT vote from %s WHERE token=%%s AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
        return self.get_query_set().extra(select={'user_vote': query},
                                          select_params=(token,))


class VotableModel(models.Model):

    objects = VotableManager()

    class Meta:
        abstract = True

    votes = generic.GenericRelation(Vote)

    vote_total = property(lambda self: self.total_upvotes-self.total_downvotes)

    def add_vote(self, token, vote):
        voteobj, created = self.votes.get_or_create(token=token,
            defaults={'vote':vote, 'content_object':self})
        if not created:
            voteobj.vote = vote
            voteobj.save()

    def remove_vote(self, token):
        self.votes.filter(token=token).delete()
