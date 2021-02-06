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


def logout(request):
    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not 'token' in request.POST:
        return HttpResponseBadRequest('Please specify token.')

    token = request.POST.get('token')

    profile = Profile.objects.filter(log_token=token, log_expire__gt=time.time())

    if not profile.exists():
        return HttpResponseBadRequest('Requête expirée.')

    profile = profile.get()

    profile.log_expire = -1
    profile.save()

    return HttpResponse('')