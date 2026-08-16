def limit_total_votes(num):
    # imported lazily: this module is imported before the app registry is
    # ready, so importing the vote model at module level would fail
    from secretballot.utils import get_vote_model  # noqa: PLC0415

    Vote = get_vote_model()  # noqa: N806 -- holds a class, not an instance

    def total_vote_limiter(request, content_type, object_id, vote):
        return (
            Vote.objects.filter(
                content_type=content_type,
                token=request.secretballot_token,
            ).count()
            < num
        )

    return total_vote_limiter


def enable_voting_on(  # noqa: C901, PLR0913, PLR0917 -- public API, kwargs are all user-facing
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
    # imported lazily: this module is imported before the app registry is
    # ready, so importing Django/app models at module level would fail
    from django.contrib.contenttypes.fields import GenericRelation  # noqa: PLC0415
    from django.contrib.contenttypes.models import ContentType  # noqa: PLC0415
    from django.core.exceptions import ImproperlyConfigured  # noqa: PLC0415
    from django.db.models import Manager  # noqa: PLC0415
    from django.db.models import OuterRef  # noqa: PLC0415
    from django.db.models import Subquery  # noqa: PLC0415

    from secretballot.utils import get_vote_model  # noqa: PLC0415

    Vote = get_vote_model()  # noqa: N806 -- holds a class, not an instance

    def add_vote(self, token, vote):
        voteobj, created = getattr(self, votes_name).get_or_create(
            token=token,
            defaults={"vote": vote, "content_object": self},
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
            db_table = self.model._meta.db_table  # noqa: SLF001
            pk_name = self.model._meta.pk.attname  # noqa: SLF001
            opts = ContentType.objects._get_opts(  # noqa: SLF001
                self.model,
                for_concrete_model=True,
            )
            content_type_table = ContentType._meta.db_table  # noqa: SLF001
            # the interpolated values below are all Django-internal metadata
            # (table names, pk attname, app_label/model_name, -1/1 literals),
            # never request/user input, so there is no injection surface here
            content_type_id_query = (
                f"(SELECT id FROM {content_type_table} "  # noqa: S608
                f"WHERE app_label='{opts.app_label}' AND model='{opts.model_name}')"
            )
            vote_query = (
                f"(SELECT COUNT(*) from {Vote._meta.db_table} WHERE vote={{}} "  # noqa: S608, SLF001
                f"AND object_id={db_table}.{pk_name} "
                f"AND content_type_id={content_type_id_query})"
            )
            downvote_query = vote_query.format(-1)
            upvote_query = vote_query.format(1)
            return (
                super()
                .get_queryset()
                .extra(  # noqa: S610
                    select={upvotes_name: upvote_query, downvotes_name: downvote_query},
                )
            )

        def from_token(self, token):
            pk_column = self.model._meta.pk.attname  # noqa: SLF001
            votes_vote_column = f"{votes_name}__vote"
            votes_token_column = f"{votes_name}__token"
            return self.get_queryset().annotate(
                user_vote=Subquery(
                    self.model.objects.filter(
                        **{votes_token_column: token, pk_column: OuterRef(pk_column)},
                    ).values(
                        votes_vote_column,
                    ),
                ),
            )

        def from_request(self, request):
            if not hasattr(request, "secretballot_token"):
                msg = (
                    "To use secretballot a SecretBallotMiddleware must "
                    "be installed. (see secretballot/middleware.py)"
                )
                raise ImproperlyConfigured(msg)
            return self.from_token(request.secretballot_token)

    # If 'objects' is the manager_name, then remove if from managers_map
    # and lets VotableManager have the name 'objects'.
    vm = VotableManager()
    cls._meta.local_managers[:] = (
        manager for manager in cls._meta.local_managers if manager.name != manager_name
    )
    cls.add_to_class(manager_name, vm)
    cls.add_to_class(votes_name, GenericRelation(Vote))
    cls.add_to_class(total_name, property(get_total))
    cls.add_to_class(add_vote_name, add_vote)
    cls.add_to_class(remove_vote_name, remove_vote)
    cls._secretballot_enabled = True
