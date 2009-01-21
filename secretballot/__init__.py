from secretballot.models import Vote
from functools import partial

def total_vote_limiter(request, content_type, object_id, vote, num):
    return Vote.objects.filter(content_type=content_type, 
                                token=request.secretballot_token).count() < num

def limit_total_votes(num_votes):
    return partial(total_vote_limiter, num=num_votes)
