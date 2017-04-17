# -*- coding: utf-8 -*-
from hashlib import md5

from django import VERSION

a, b = VERSION[:2]
if (a < 1) or (a == 1 and b < 10):
    Mixin = object
else:
    from django.utils.deprecation import MiddlewareMixin
    Mixin = MiddlewareMixin


class SecretBallotMiddleware(Mixin):
    def process_request(self, request):
        request.secretballot_token = self.generate_token(request)

    def generate_token(self, request):
        raise NotImplementedError


class SecretBallotIpMiddleware(SecretBallotMiddleware):
    def generate_token(self, request):
        return request.META['REMOTE_ADDR']


class SecretBallotIpUseragentMiddleware(SecretBallotMiddleware):
    def generate_token(self, request):
        s = u"".join((request.META['REMOTE_ADDR'], request.META.get('HTTP_USER_AGENT', '')))
        return md5(s.encode('utf-8')).hexdigest()
