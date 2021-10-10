# -*- coding: utf-8 -*-
from hashlib import md5


class SecretBallotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.secretballot_token = self.generate_token(request)

        return self.get_response(request)

    def generate_token(self, request):
        raise NotImplementedError


class SecretBallotIpMiddleware(SecretBallotMiddleware):
    def generate_token(self, request):
        return request.META["REMOTE_ADDR"]


class SecretBallotUserIdMiddleware(SecretBallotMiddleware):
    """
    This Middleware is useful if you want to implement anonymous voting,
    but only for logged in users.

    As the token is generated based on the user ID, this middleware
    should only be used on pages where the user is logged in.
    """

    def generate_token(self, request):
        return str(request.user.id)


class SecretBallotIpUseragentMiddleware(SecretBallotMiddleware):
    def generate_token(self, request):
        s = u"".join((request.META["REMOTE_ADDR"], request.META.get("HTTP_USER_AGENT", "")))
        return md5(s.encode("utf-8")).hexdigest()
