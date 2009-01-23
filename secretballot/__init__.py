from secretballot.models import Vote

def limit_total_votes(num):
    def total_vote_limiter(request, content_type, object_id, vote):
        return Vote.objects.filter(content_type=content_type, 
                               token=request.secretballot_token).count() < num
    return total_vote_limiter
