import json
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Sum
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.test import TestCase

import pytest

from secretballot import enable_voting_on
from secretballot import views
from secretballot.middleware import SecretBallotIpMiddleware
from secretballot.middleware import SecretBallotIpUseragentMiddleware
from secretballot.middleware import SecretBallotMiddleware

from .models import AnotherLink
from .models import Link
from .models import NonAutomaticEnabledModel
from .models import WeirdLink


def get_response_empty(request):
    return HttpResponse()


class MiddlewareTestCase(TestCase):
    def test_ip_middleware(self):
        mw = SecretBallotIpMiddleware(get_response_empty)

        r = HttpRequest()
        r.META["REMOTE_ADDR"] = "1.2.3.4"
        mw(r)
        assert r.secretballot_token == "1.2.3.4"  # noqa:  S105

    def test_ip_ua_middleware(self):
        mw = SecretBallotIpUseragentMiddleware(get_response_empty)

        # basic token
        r = HttpRequest()
        r.META["REMOTE_ADDR"] = "1.2.3.4"
        r.META["HTTP_USER_AGENT"] = "Firefox"
        mw(r)
        ff_token = r.secretballot_token

        # same one
        r = HttpRequest()
        r.META["REMOTE_ADDR"] = "1.2.3.4"
        r.META["HTTP_USER_AGENT"] = "Firefox"
        mw(r)
        ff_token2 = r.secretballot_token

        assert ff_token == ff_token2

        # different one
        r = HttpRequest()
        r.META["REMOTE_ADDR"] = "1.2.3.4"
        r.META["HTTP_USER_AGENT"] = "Chrome"
        mw(r)
        chrome_token = r.secretballot_token

        assert ff_token != chrome_token

        # blank one
        r = HttpRequest()
        r.META["REMOTE_ADDR"] = "1.2.3.4"
        r.META["HTTP_USER_AGENT"] = ""
        mw(r)
        blank_token = r.secretballot_token

        assert ff_token != blank_token

    def test_no_token(self):
        mw = SecretBallotMiddleware(get_response_empty)
        with pytest.raises(NotImplementedError):
            mw(HttpRequest())

    def test_unicode_token(self):
        mw = SecretBallotIpUseragentMiddleware(get_response_empty)
        r = HttpRequest()
        r.META["REMOTE_ADDR"] = "1.2.3.4"
        r.META["HTTP_USER_AGENT"] = "Orange España"
        mw(r)
        token = r.secretballot_token

        assert token == "fdb9f3e35ac8355e1e97f338f0ede097"  # noqa:  S105


class TestVoting(TestCase):
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


class TestVotingWithRenamedFields(TestCase):
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


class TestVoteView(TestCase):
    def _req(self):
        r = HttpRequest()
        r.secretballot_token = "1.2.3.4"  # noqa:  S105
        return r

    def test_no_token(self):
        r = HttpRequest()
        with pytest.raises(ImproperlyConfigured):
            views.vote(r, Link, 1, 1)

    def test_bad_content_type(self):
        r = self._req()
        # invalid content_type
        with pytest.raises(ValueError):  # noqa: PT011
            views.vote(r, 0, 1, 1)

    def test_model_content_type(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        views.vote(r, Link, link.id, 1)
        assert Link.objects.get().vote_total == 1

        # Test with custom manager name
        other_link = AnotherLink.objects.create(url="https://google.com")
        views.vote(r, AnotherLink, other_link.id, 1)
        assert AnotherLink.ballot_custom_manager.get().vote_total == 1

    def test_string_content_type(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        views.vote(r, "tests.Link", link.id, 1)
        assert Link.objects.get().vote_total == 1

        # Test with custom manager name
        other_link = AnotherLink.objects.create(url="https://google.com")
        views.vote(r, "tests.AnotherLink", other_link.id, 1)
        assert AnotherLink.ballot_custom_manager.get().vote_total == 1

    def test_content_type_content_type(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        ctype = ContentType.objects.get(model="link")
        views.vote(r, ctype, link.id, 1)
        assert Link.objects.get().vote_total == 1

    def test_vote_404(self):
        r = self._req()
        with pytest.raises(Http404):
            views.vote(r, Link, 1, 1)

    def test_can_vote_test(self):
        r = self._req()
        Link.objects.create(url="https://google.com")

        def can_vote_test(request, content_type, object_id, vote):
            return True

        views.vote(r, Link, 1, 1, can_vote_test=can_vote_test)

        def never(request, content_type, object_id, vote):
            return False

        forbidden = views.vote(r, Link, 1, 1, can_vote_test=never)
        assert forbidden.status_code == 403  # noqa: PLR2004

    def test_vote_update(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        views.vote(r, Link, link.id, 1)
        views.vote(r, Link, link.id, -1)  # update
        assert Link.objects.get().vote_total == -1

        # Test with custom manager
        other_link = AnotherLink.objects.create(url="https://google.com")
        views.vote(r, AnotherLink, other_link.id, 1)
        views.vote(r, AnotherLink, other_link.id, -1)  # update
        assert AnotherLink.ballot_custom_manager.get().vote_total == -1

    def test_vote_delete(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        views.vote(r, Link, link.id, 1)
        views.vote(r, Link, link.id, 0)  # delete
        assert Link.objects.get().vote_total == 0

        # Test with custom manager
        other_link = AnotherLink.objects.create(url="https://google.com")
        views.vote(r, AnotherLink, other_link.id, 1)
        views.vote(r, AnotherLink, other_link.id, 0)  # update
        assert AnotherLink.ballot_custom_manager.get().vote_total == 0

    def test_vote_redirect(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        resp = views.vote(r, Link, link.id, 1, redirect_url="/thanks/")
        assert resp.status_code == 302  # noqa: PLR2004
        assert resp.url == "/thanks/"

    def test_vote_template(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        resp = views.vote(r, Link, link.id, 1, template_name="vote.html")
        assert resp.status_code == 200  # noqa: PLR2004
        assert b"voted" in resp.content
        assert b"total_upvotes=1" in resp.content
        # TODO: test extra context and context processors?

    def test_vote_default_json(self):
        r = self._req()
        link = Link.objects.create(url="https://google.com")
        resp = views.vote(r, Link, link.id, 1)
        assert resp.status_code == 200  # noqa: PLR2004
        assert json.loads(resp.content.decode("utf8"))["num_votes"] == 1


class AddSecretBallotManagerTestCase(TestCase):
    """
    secret_ballot manager should be added to model specified
    in enable_voting_on(). Use `objects` as default for the
    manager's name.
    """

    def test_object_manager_is_added_to_class(self):
        assert any(
            manager.__class__.__name__ == "VotableManager"
            for manager in Link._meta.managers  # noqa: SLF001
        )

    def test_object_manager_with_custom_name(self):
        assert hasattr(AnotherLink, "ballot_custom_manager")

    def test_no_db_access_when_getting_queryset(self):
        with patch("django.db.backends.utils.CursorWrapper") as db_mock:
            db_mock.side_effect = RuntimeError("Tried to access database")

            enable_voting_on(NonAutomaticEnabledModel)

            NonAutomaticEnabledModel.objects.get_queryset()

            db_mock.assert_not_called()
