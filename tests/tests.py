from django.test import TestCase
from django.http import HttpRequest

from secretballot.middleware import SecretBallotIpMiddleware, SecretBallotIpUseragentMiddleware


class MiddlewareTestCase(TestCase):
    def test_ip_middleware(self):
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        SecretBallotIpMiddleware().process_request(r)
        assert r.secretballot_token == '1.2.3.4'

    def test_ip_ua_middleware(self):
        # basic token
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Firefox'
        SecretBallotIpUseragentMiddleware().process_request(r)
        ff_token = r.secretballot_token

        # same one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Firefox'
        SecretBallotIpUseragentMiddleware().process_request(r)
        ff_token2 = r.secretballot_token

        assert ff_token == ff_token2

        # different one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Chrome'
        SecretBallotIpUseragentMiddleware().process_request(r)
        chrome_token = r.secretballot_token

        assert ff_token != chrome_token

        # blank one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = ''
        SecretBallotIpUseragentMiddleware().process_request(r)
        blank_token = r.secretballot_token

        assert ff_token != blank_token
