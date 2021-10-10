default_app_config = "%s.apps.AppConfig" % __name__


def limit_total_votes(num):
    from secretballot.utils import get_vote_model

    Vote = get_vote_model()

    def total_vote_limiter(request, content_type, object_id, vote):
        return Vote.objects.filter(content_type=content_type, token=request.secretballot_token).count() < num

    return total_vote_limiter


def enable_voting_on(
    cls,
    manager_name="objects",
    votes_name="votes",
    upvotes_name="total_upvotes",
    downvotes_name="total_downvotes",
    total_name="vote_total",
    add_vote_name="add_vote",
    remove_vote_name="remove_vote",
    base_manager=None,
):
    from django.contrib.contenttypes.fields import GenericRelation
    from django.contrib.contenttypes.models import ContentType
    from django.core.exceptions import ImproperlyConfigured
    from django.db.models import Manager, OuterRef, Subquery

    from secretballot.utils import get_vote_model

    Vote = get_vote_model()

    def add_vote(self, token, vote):
        voteobj, created = getattr(self, votes_name).get_or_create(
            token=token, defaults={"vote": vote, "content_object": self}
        )
        if not created:
            voteobj.vote = vote
            voteobj.save()

    def remove_vote(self, token):
        getattr(self, votes_name).filter(token=token).delete()

    # gets added to the class as a property, not under this name
    def get_total(self):
        return getattr(self, upvotes_name) - getattr(self, downvotes_name)

    if base_manager is None:
        if hasattr(cls, manager_name):
            base_manager = getattr(cls, manager_name).__class__
        else:
            base_manager = Manager

    class VotableManager(base_manager):

        use_for_related_fields = True

        def get_queryset(self):
            db_table = self.model._meta.db_table
            pk_name = self.model._meta.pk.attname
            opts = ContentType.objects._get_opts(self.model, for_concrete_model=True)
            content_type_id_query = "(SELECT id FROM {} WHERE app_label='{}' AND model='{}')".format(
                ContentType._meta.db_table, opts.app_label, opts.model_name
            )
            vote_query = "(SELECT COUNT(*) from {} WHERE vote={{}} AND object_id={}.{} AND content_type_id={})".format(
                Vote._meta.db_table, db_table, pk_name, content_type_id_query
            )
            downvote_query = vote_query.format(-1)
            upvote_query = vote_query.format(1)
            return (
                super(VotableManager, self)
                .get_queryset()
                .extra(select={upvotes_name: upvote_query, downvotes_name: downvote_query})
            )

        def from_token(self, token):
            pk_column = self.model._meta.pk.attname
            votes_vote_column = "{}__vote".format(votes_name)
            votes_token_column = "{}__token".format(votes_name)
            return self.get_queryset().annotate(
                user_vote=Subquery(
                    self.model.objects.filter(**{votes_token_column: token, pk_column: OuterRef(pk_column)}).values(
                        votes_vote_column
                    )
                )
            )

        def from_request(self, request):
            if not hasattr(request, "secretballot_token"):
                raise ImproperlyConfigured(
                    "To use secretballot a SecretBallotMiddleware must "
                    "be installed. (see secretballot/middleware.py)"
                )
            return self.from_token(request.secretballot_token)

    # If 'objects' is the manager_name, then remove if from managers_map
    # and lets VotableManager have the name 'objects'.
    vm = VotableManager()
    cls._meta.local_managers[:] = (manager for manager in cls._meta.local_managers if not manager.name == manager_name)
    cls.add_to_class(manager_name, vm)
    cls.add_to_class(votes_name, GenericRelation(Vote))
    cls.add_to_class(total_name, property(get_total))
    cls.add_to_class(add_vote_name, add_vote)
    cls.add_to_class(remove_vote_name, remove_vote)
    setattr(cls, "_secretballot_enabled", True)
