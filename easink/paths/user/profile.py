import json
import time

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

from djangoProject.objects.Profile import Profile
from djangoProject.utils import security_utils


def profile(request):
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

    auth = {'token': profile.log_token, 'expire': profile.log_expire}
    user_info = {'email': user.email, 'username': user.username, 'date_joined': user.date_joined}

    json_data = serializers.serialize('json', [user.profile, ])
    new_data = json.loads(json_data)
    new_data = new_data[0]['fields']

    profile_data = {'auth': auth, 'user': user_info, 'profile': new_data}

    return JsonResponse(profile_data)