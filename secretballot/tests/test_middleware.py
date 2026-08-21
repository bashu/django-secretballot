from django.http import HttpRequest
from django.http import HttpResponse
from django.test import TestCase

import pytest

from secretballot.middleware import SecretBallotIpMiddleware
from secretballot.middleware import SecretBallotIpUseragentMiddleware
from secretballot.middleware import SecretBallotMiddleware


def get_response_empty(request):
    return HttpResponse()


class SecretBallotMiddlewareTest(TestCase):
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
