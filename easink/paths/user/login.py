import json
import time

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

from djangoProject.utils import security_utils


def login(request):
    if security_utils.rate_limited(request, 'login', 10):
        return HttpResponseBadRequest('Veuillez patienter avant chaque tentative de connexion.')

    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not "email" in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier une adresse email.')

    if not "password" in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier un mot de passe.')

    remember = 0

    if "remember" in request.POST:
        if request.POST.get("remember") == 1:
            remember = 1

    email = request.POST.get("email")
    password = request.POST.get("password")

    try:
        user = User.objects.filter(email=email)

        if not user.exists():
            raise Exception('Unknown email')

        user = user.get()

        usp = make_password(user.password)
        check = check_password(user.password, usp)

        if not check:
            raise Exception('invalid password')
    except Exception as e:
        print(e)
        return HttpResponseBadRequest('Email ou mot de passe incorrect. Veuillez vérifier vos informations.')

    if not user.is_active:
        return HttpResponseBadRequest('Ce compte utilisateur n\'est pas actif.')

    profile = user.profile
    if len(profile.verify_token) > 0:
        return HttpResponseBadRequest('Veuillez vérifier votre adresse email depuis l\'email que vous avez reçu.')

    profile.log_token = security_utils.generate_token()

    if remember == 0:
        profile.log_expire = time.time() + 86400
    else:
        profile.log_expire = time.time() + (86400 * 365)

    profile.save()

    auth = {'token': profile.log_token, 'expire': profile.log_expire}
    user_info = {'email': user.email, 'username': user.username, 'date_joined': user.date_joined}

    json_data = serializers.serialize('json', [user.profile, ])
    new_data = json.loads(json_data)
    new_data = new_data[0]['fields']

    profile_data = {'auth': auth, 'user': user_info, 'profile': new_data}

    return JsonResponse(profile_data)