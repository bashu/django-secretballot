from django.test import TestCase
from django.http import HttpRequest

from secretballot.middleware import (SecretBallotMiddleware,
                                     SecretBallotIpMiddleware,
                                     SecretBallotIpUseragentMiddleware)
from .models import Link, WeirdLink


class MiddlewareTestCase(TestCase):
    def test_ip_middleware(self):
        mw = SecretBallotIpMiddleware()
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        mw.process_request(r)
        assert r.secretballot_token == '1.2.3.4'

    def test_ip_ua_middleware(self):
        mw = SecretBallotIpUseragentMiddleware()

        # basic token
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Firefox'
        mw.process_request(r)
        ff_token = r.secretballot_token

        # same one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Firefox'
        mw.process_request(r)
        ff_token2 = r.secretballot_token

        assert ff_token == ff_token2

        # different one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Chrome'
        mw.process_request(r)
        chrome_token = r.secretballot_token

        assert ff_token != chrome_token

        # blank one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = ''
        mw.process_request(r)
        blank_token = r.secretballot_token

        assert ff_token != blank_token

    def test_no_token(self):
        mw = SecretBallotMiddleware()
        with self.assertRaises(NotImplementedError):
            mw.process_request(HttpRequest())


class TestVoting(TestCase):

    def test_add_vote(self):
        l = Link.objects.create(url='https://google.com')
        assert Link.objects.get().vote_total == 0

        l.add_vote('1.2.3.4', 1)
        assert Link.objects.get().vote_total == 1

        l.add_vote('1.2.3.5', 1)
        assert Link.objects.get().vote_total == 2

        l.add_vote('1.2.3.6', -1)
        assert Link.objects.get().vote_total == 1

    def test_up_and_down(self):
        l = Link.objects.create(url='https://google.com')

        l.add_vote('1.2.3.4', 1)
        l.add_vote('1.2.3.6', -1)

        l = Link.objects.get()
        assert l.total_upvotes == 1
        assert l.total_downvotes == 1
        assert l.vote_total == 0

    def test_remove_vote(self):
        l = Link.objects.create(url='https://google.com')
        assert Link.objects.get().vote_total == 0

        l.add_vote('1.2.3.4', 1)
        l.add_vote('1.2.3.5', 1)
        assert Link.objects.get().vote_total == 2

        l.remove_vote('1.2.3.5')
        assert Link.objects.get().vote_total == 1

    def test_from_token(self):
        b = Link.objects.create(url='https://bing.com')
        g = Link.objects.create(url='https://google.com')
        y = Link.objects.create(url='https://yahoo.com')

        # no vote on bing, +1 on google, -1 yahoo
        g.add_vote('1.2.3.4', 1)
        y.add_vote('1.2.3.4', -1)

        sorted_links = Link.objects.from_token('1.2.3.4').order_by('url')
        assert sorted_links[0].user_vote == None     # bing
        assert sorted_links[1].user_vote == 1        # google
        assert sorted_links[2].user_vote == -1       # yahoo


    def test_from_request(self):
        b = Link.objects.create(url='https://bing.com')
        g = Link.objects.create(url='https://google.com')
        y = Link.objects.create(url='https://yahoo.com')

        # no vote on bing, +1 on google, -1 yahoo
        g.add_vote('1.2.3.4', 1)
        y.add_vote('1.2.3.4', -1)

        # would be set by middleware
        r = HttpRequest()
        r.secretballot_token = '1.2.3.4'

        sorted_links = Link.objects.from_request(r).order_by('url')
        assert sorted_links[0].user_vote == None     # bing
        assert sorted_links[1].user_vote == 1        # google
        assert sorted_links[2].user_vote == -1       # yahoo


class TestVotingWithRenamedFields(TestCase):

    def test_everything_is_renamed(self):
        # one big example to surface any issues in renaming fields
        l = WeirdLink.objects.create(url='https://google.com')
        l.add_v('1.2.3.4', 1)
        l.add_v('1.2.3.5', -1)
        l = WeirdLink.objects.get()
        assert l.v_total == 0
        assert l.total_upvs == 1
        assert l.total_downvs == 1
        assert l.vs.all()
        assert l._secretballot_enabled is True
