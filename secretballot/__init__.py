import hashlib

def ip_token(request):
    return request.META['REMOTE_ADDR']

def ip_useragent_token(request):
     s = ''.join((request.META['REMOTE_ADDR'], request.META['HTTP_USER_AGENT']))
     return hashlib.md5(s).hexdigest()
    
