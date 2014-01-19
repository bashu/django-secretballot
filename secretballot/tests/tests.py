import unittest
from secretballot.middleware import *
from django.http import HttpRequest


class UserAgentTest(unittest.TestCase):
    def test_missing_user_agent(self):
        """Requests missing USER-AGENT should not raise KeyError"""
        req = HttpRequest()
        req.META['REMOTE_ADDR'] = '158.143.233.172'
        mw = SecretBallotIpUseragentMiddleware()
        h = mw.generate_token(req)
        self.assertEqual(h, "ae2f59bc09d8ca94e19d5bae01a535c3")
