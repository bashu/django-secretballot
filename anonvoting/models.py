from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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
        downvote_query = '(SELECT COUNT(*) from anonvoting_vote WHERE vote=-1 AND object_id=%s.%s AND content_type_id=%s)' % (db_table, pk_name, content_type)
        upvote_query = '(SELECT COUNT(*) from anonvoting_vote WHERE vote=1 AND object_id=%s.%s AND content_type_id=%s)' % (db_table, pk_name, content_type)
        return super(VotableManager, self).get_query_set().extra(
            select={'upvotes': upvote_query, 'downvotes': downvote_query})

    def from_token(self, token):
        db_table = self.model._meta.db_table
        pk_name = self.model._meta.pk.attname
        content_type = ContentType.objects.get_for_model(self.model).id
        query = '(SELECT vote from anonvoting_vote WHERE token=%%s AND object_id=%s.%s AND content_type_id=%s)' % (db_table, pk_name, content_type)
        return self.get_query_set().extra(select={'user_vote': query},
                                          select_params=(token,))

    
class VotableModel(models.Model):
    
    objects = VotableManager()
    
    class Meta:
        abstract = True

    votes = generic.GenericRelation(Vote)
    
    # store (downvotes, upvotes)
    _vote_counts = None
    def _get_vote_counts(self):
        if not self._vote_counts:
            votes = list(self.votes.values_list('vote', flat=True))
            downvotes = votes.count(-1)
            self._vote_counts = (downvotes, len(votes)-downvotes)
        return self._vote_counts
    vote_counts = property(_get_vote_counts)
    vote_total = property(lambda self: self.vote_counts[1]-self.vote_counts[0])
    downvote_total = property(lambda self: self.vote_counts[0])
    upvote_total = property(lambda self: self.vote_counts[1])
    
    def get_vote(self, token):
        try:
            return self.votes.get(ip=token).vote
        except models.DoesNotExist:
            return None
        
    def add_vote(self, token, vote):
        voteobj, created = self.votes.get_or_create(token=token,
            defaults={'vote':vote, 'content_object':self})
        if not created:
            voteobj.vote = vote
            voteobj.save()
        
    def remove_vote(self, token):
        self.votes.filter(token=token).delete()
