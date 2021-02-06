# TODO comments
import collections
import time

from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

# TODO comments
from djangoProject.objects.Profile import Profile
from djangoProject.queues import artists_manager
from djangoProject.utils import math_utils


def artists(request):
    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not 'token' in request.POST:
        return HttpResponseBadRequest('Please specify token.')

    token = request.POST.get('token')

    profile = Profile.objects.filter(log_token=token, log_expire__gt=time.time())

    if not profile.exists():
        return HttpResponseBadRequest('Requête expirée.')

    profile = profile.get()

    long = profile.longitude
    lat = profile.latitude

    if long == "" or lat == "":
        # Classic
        long = 0
        lat = 0
    else:
        long = float(long)
        lat = float(lat)

    artists_near = {}
    i_max = 50 # Maybe we will edit this in the future..
    i = 0

    # Filters
    filter_name = None
    filter_style = None
    filter_localization = None

    if 'name' in request.POST:
        filter_name = request.POST.get('name')

    if 'style' in request.POST:
        filter_style = request.POST.get('style')

    if 'localization' in request.POST:
        filter_localization = request.POST.get('localization')

    for artist in artists_manager.artists:
        if filter_name is not None:
            if filter_name not in artist.shop_name:
                continue

        if filter_style is not None:
            if filter_style not in artist.styles:
                continue

        if filter_localization is not None:
            if filter_localization not in artist.shop_localization:
                continue

        i += 1
        if i >= i_max:
            break

        artist = artists_manager.artists[artist]

        m = math_utils.distance(lat, long, artist.shop_lat, artist.shop_long)
        dict = artist.__dict__
        dict.update({'distance': math_utils.format_dist(dict.distance)})

        artists_near[m] = dict

    dc = collections.OrderedDict(sorted(artists_near.items()))

    return JsonResponse(dc)