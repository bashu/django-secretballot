from django.db import models
import secretballot


class Link(models.Model):
    url = models.URLField()

secretballot.enable_voting_on(Link)


# used for testing field renames
class WeirdLink(models.Model):
    url = models.URLField()

secretballot.enable_voting_on(WeirdLink,
                              votes_name='vs',
                              upvotes_name='total_upvs',
                              downvotes_name='total_downvs',
                              total_name='v_total',
                              add_vote_name='add_v',
                              remove_vote_name='remove_v',
                              )
# TODO?: base_manager?


# Used for testing custom manager_name
class AnotherLink(models.Model):
    url = models.URLField()

secretballot.enable_voting_on(AnotherLink,
                              manager_name='ballot_custom_manager'
                              )
