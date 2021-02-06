# TODO comments
import collections
import time

from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

# TODO comments
from djangoProject.objects.Profile import Profile
from djangoProject.queues import artists_manager
from djangoProject.utils import math_utils


def artist_info(request):
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
        if artist.unique_id == uuid:
            art = artist
            break

    if art is None:
        return HttpResponseBadRequest('Artiste inconnu.')

    long = profile.longitude
    lat = profile.latitude

    if long == "" or lat == "":
        # Classic
        long = 0
        lat = 0
    else:
        long = float(long)
        lat = float(lat)

    m = math_utils.distance(lat, long, art.shop_lat, art.shop_long)
    dict = art.__dict__
    dict.update({'distance': math_utils.format_dist(dict.distance)})

    return JsonResponse(dict)