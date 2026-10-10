import json

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.http import HttpRequest
from django.test import TestCase

import pytest

from secretballot import views

from .models import AnotherLink
from .models import Link


class SecretBallotViewTest(TestCase):
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
