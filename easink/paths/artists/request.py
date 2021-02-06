import json
import time

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

from djangoProject.objects.ArtistRequest import ArtistRequest
from djangoProject.objects.Profile import Profile
from djangoProject.utils import security_utils


def request(request):
    if security_utils.rate_limited(request, 'request', 10):
        return HttpResponseBadRequest('Veuillez patienter avant chaque tentative de requête d\'ajout.')

    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not 'token' in request.POST:
        return HttpResponseBadRequest('Please specify token.')

    token = request.POST.get('token')

    profile = Profile.objects.filter(log_token=token, log_expire__gt=time.time())

    if not profile.exists():
        return HttpResponseBadRequest('Requête expirée.')

    profile = profile.get()
    user = profile.user

    #okok
    if not 'artist-name' in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier le nom de l\'artiste.')

    if not 'shop-name' in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier le nom du shop.')

    if not 'city' in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier la ville du shop.')

    instagram = ""

    if 'instagram' in request.POST:
        instagram = request.POST.get('instagram')

    artist_name = request.POST.get('artist-name')
    shop_name = request.POST.get('shop-name')
    city = request.POST.get('city')
    author = profile.unique_name

    artist_request = ArtistRequest.objects.create(author=author, artist_name=artist_name, shop_name=shop_name, city=city)

    return HttpResponse('La demande d\'ajout de l\'artiste a bien été envoyée.')