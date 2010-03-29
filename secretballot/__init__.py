__author__ = "James Turk (jturk@sunlightfoundation.com)"
__version__ = "0.2.3"
__copyright__ = "Copyright (c) 2009 Sunlight Labs"
__license__ = "BSD"

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

def limit_total_votes(num):
    from secretballot.models import Vote
    def total_vote_limiter(request, content_type, object_id, vote):
        return Vote.objects.filter(content_type=content_type, 
                               token=request.secretballot_token).count() < num
    return total_vote_limiter


def enable_voting_on(cls, manager_name='objects',
                    votes_name='votes',
                    upvotes_name='total_upvotes',
                    downvotes_name='total_downvotes',
                    total_name='vote_total',
                    add_vote_name='add_vote',
                    remove_vote_name='remove_vote',
                    base_manager=None):
    from secretballot.models import Vote
    VOTE_TABLE = Vote._meta.db_table

    def add_vote(self, token, vote):
        voteobj, created = self.votes.get_or_create(token=token,
            defaults={'vote':vote, 'content_object':self})
        if not created:
            voteobj.vote = vote
            voteobj.save()

    def remove_vote(self, token):
        self.votes.filter(token=token).delete()

    def get_total(self):
        return getattr(self, upvotes_name) - getattr(self, downvotes_name)

    if base_manager is None:
        if hasattr(cls, manager_name):
            base_manager = getattr(cls, manager_name).__class__
        else:
            base_manager = Manager

    class VotableManager(base_manager):

        def get_query_set(self):
            db_table = self.model._meta.db_table
            pk_name = self.model._meta.pk.attname
            content_type = ContentType.objects.get_for_model(self.model).id
            downvote_query = '(SELECT COUNT(*) from %s WHERE vote=-1 AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
            upvote_query = '(SELECT COUNT(*) from %s WHERE vote=1 AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
            return super(VotableManager, self).get_query_set().extra(
                select={upvotes_name: upvote_query,
                        downvotes_name: downvote_query})

        def from_token(self, token):
            db_table = self.model._meta.db_table
            pk_name = self.model._meta.pk.attname
            content_type = ContentType.objects.get_for_model(self.model).id
            query = '(SELECT vote from %s WHERE token=%%s AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
            return self.get_query_set().extra(select={'user_vote': query},
                                              select_params=(token,))

        def from_request(self, request):
            if not hasattr(request, 'secretballot_token'):
                raise ImproperlyConfigured('To use secretballot a SecretBallotMiddleware must be installed. (see secretballot/middleware.py)')
            return self.from_token(request.secretballot_token)


    cls.add_to_class(manager_name, VotableManager())
    cls.add_to_class(votes_name, generic.GenericRelation(Vote))
    cls.add_to_class(total_name, property(get_total))
    cls.add_to_class(add_vote_name, add_vote)
    cls.add_to_class(remove_vote_name, remove_vote)
