import codecs
import time
from pathlib import Path

import stdnum
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from email_validator import EmailNotValidError, validate_email
from stdnum.fr import siret

from djangoProject.objects.Email import Email
from djangoProject.objects.Profile import Profile
from djangoProject.queues import queue_email
from djangoProject.utils import password_utils

# TODO COMMENTS


def collect(request):
    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not 'token' in request.POST:
        return HttpResponseBadRequest('Please specify token.')

    token = request.POST.get('token')

    profile = Profile.objects.filter(log_token=token, log_expire__gt=time.time())

    if not profile.exists():
        return HttpResponseBadRequest('Requête expirée.')

    profile = profile.get()

    # Collect location
    localization(request, profile)

    profile.save()

    return HttpResponse('')


def localization(request, profile):
    if 'long' in request.POST and 'lat' in request.POST:
        print('okp')
        profile.longitude = request.POST.get('long')
        profile.latitude = request.POST.get('lat')

        profile.save()