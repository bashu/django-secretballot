from django.db.models import Sum
from django.http import HttpRequest
from django.test import TestCase

from .models import AnotherLink
from .models import Link
from .models import WeirdLink


class SecretBallotModelTest(TestCase):
    def test_add_vote(self):
        link = Link.objects.create(url="https://google.com")
        assert Link.objects.get().vote_total == 0

        link.add_vote("1.2.3.4", 1)
        assert Link.objects.get().vote_total == 1

        link.add_vote("1.2.3.5", 1)
        assert Link.objects.get().vote_total == 2  # noqa: PLR2004

        link.add_vote("1.2.3.6", -1)
        assert Link.objects.get().vote_total == 1

    def test_up_and_down(self):
        link = Link.objects.create(url="https://google.com")

        link.add_vote("1.2.3.4", 1)
        link.add_vote("1.2.3.6", -1)

        link = Link.objects.get()
        assert link.total_upvotes == 1
        assert link.total_downvotes == 1
        assert link.vote_total == 0

    def test_remove_vote(self):
        link = Link.objects.create(url="https://google.com")
        assert Link.objects.get().vote_total == 0

        link.add_vote("1.2.3.4", 1)
        link.add_vote("1.2.3.5", 1)
        assert Link.objects.get().vote_total == 2  # noqa: PLR2004

        link.remove_vote("1.2.3.5")
        assert Link.objects.get().vote_total == 1

    def test_from_token(self):
        Link.objects.create(url="https://bing.com")
        g = Link.objects.create(url="https://google.com")
        y = Link.objects.create(url="https://yahoo.com")

        # no vote on bing, +1 on google, -1 yahoo
        g.add_vote("1.2.3.4", 1)
        y.add_vote("1.2.3.4", -1)

        sorted_links = Link.objects.from_token("1.2.3.4").order_by("url")
        assert sorted_links[0].user_vote is None  # bing
        assert sorted_links[1].user_vote == 1  # google
        assert sorted_links[2].user_vote == -1  # yahoo

    def test_from_request(self):
        Link.objects.create(url="https://bing.com")
        g = Link.objects.create(url="https://google.com")
        y = Link.objects.create(url="https://yahoo.com")

        # no vote on bing, +1 on google, -1 yahoo
        g.add_vote("1.2.3.4", 1)
        y.add_vote("1.2.3.4", -1)

        # would be set by middleware
        r = HttpRequest()
        r.secretballot_token = "1.2.3.4"  # noqa: S105

        sorted_links = Link.objects.from_request(r).order_by("url")
        assert sorted_links[0].user_vote is None  # bing
        assert sorted_links[1].user_vote == 1  # google
        assert sorted_links[2].user_vote == -1  # yahoo

    def test_aggregates(self):
        b = Link.objects.create(url="https://bing.com")
        b.add_vote("1.1.1.1", 1)
        g = Link.objects.create(url="https://google.com")
        g.add_vote("1.1.1.1", 1)
        g.add_vote("2.2.2.2", 1)
        g.add_vote("3.3.3.3", -1)
        g.add_vote("4.4.4.4", 1)

        assert (
            Link.objects.filter(url="https://google.com").aggregate(
                total_votes=Sum("votes__vote"),
            )["total_votes"]
            == 2  # noqa: PLR2004
        )

    def test_everything_is_renamed(self):
        # one big example to surface any issues in renaming fields
        link = WeirdLink.objects.create(url="https://google.com")
        link.add_v("1.2.3.4", 1)
        link.add_v("1.2.3.5", -1)
        link = WeirdLink.objects.get()
        assert link.v_total == 0
        assert link.total_upvs == 1
        assert link.total_downvs == 1
        assert link.vs.all()
        assert link._secretballot_enabled is True  # noqa: SLF001

    def test_str_method_works_with_non_ascii(self):
        link = WeirdLink.objects.create(url="https//other.url", title="Orangé España")
        link.add_v("1.2.3.4", 1)
        link = WeirdLink.objects.get(id=link.id)
        assert link.v_total == 1
        vote = link.vs.first()
        vote_str_out = vote.__str__()
        assert vote_str_out == "+1 from 1.2.3.4 on Orangé España"

    def test_manager_with_custom_name(self):
        # If you provide a custom manager_name, then the vote fields
        # are available through that manager
        link = AnotherLink.objects.create(url="https://google.com")
        link.add_vote("1.2.3.4", 1)
        link.add_vote("1.2.3.5", -1)
        link = AnotherLink.ballot_custom_manager.get()
        assert link.vote_total == 0
        assert link.total_upvotes == 1
        assert link.total_downvotes == 1
        assert link.votes.all()
        assert link._secretballot_enabled is True  # noqa: SLF001
