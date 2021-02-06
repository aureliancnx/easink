# TODO comments
import collections
import json
import time

from django.core import serializers
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

# TODO comments
from djangoProject.objects.Comment import Comment
from djangoProject.objects.Profile import Profile
from djangoProject.queues import artists_manager
from djangoProject.utils import math_utils, security_utils


def artist_comments(request):
    if security_utils.rate_limited(request, 'comments', 1):
        return HttpResponseBadRequest('Veuillez patienter avant chaque requête.')

    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not 'token' in request.POST:
        return HttpResponseBadRequest('Please specify token.')

    if not 'uuid' in request.POST:
        return HttpResponseBadRequest('Please specify uuid.')

    token = request.POST.get('token')
    uuid = request.POST.get('uuid')

    profile = Profile.objects.filter(log_token=token, log_expire__gt=time.time())

    if not profile.exists():
        return HttpResponseBadRequest('Requête expirée.')

    profile = profile.get()

    art = None

    for artist in artists_manager.artists:
        artp = artists_manager.artists[artist]
        if artp.unique_id == uuid:
            art = artp
            break

    if art is None:
        return HttpResponseBadRequest('Artiste inconnu.')

    res = {}
    comments = Comment.objects.filter(artist_id=art.unique_id, status=1).order_by('-time')
    i = 0

    for comment in comments:
        json_data = serializers.serialize('json', [comment, ])
        new_data = json.loads(json_data)
        new_data = new_data[0]['fields']

        res[i] = new_data
        i += 1

    print(res)

    return JsonResponse(res)