import codecs
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
from djangoProject.utils import password_utils, security_utils


# TODO COMMENTS


def verify(request, token):
    if security_utils.rate_limited(request, 'verify-email', 10):
        return render(request, 'verify-error.html', {'message': 'Veuillez patienter entre chaque requête.'})

    message = "Votre compte a été validé. Vous pouvez désormais vous connecter depuis l'application."

    # Check token
    profile = Profile.objects.filter(verify_token=token)

    if not profile.exists():
        return render(request, 'verify-error.html', {'message': 'Token de vérification inconnu. Votre compte est peut être déjà validé.'})

    profile = profile.get()
    profile.verify_token = ""
    profile.save()

    user = profile.user

    send_welcome_email(user.username, user.email)

    # Return page
    return render(request, 'verify-success.html', {'message': message})


def send_welcome_email(username, email):
    with codecs.open('mail-templates/account-welcome.html', 'r', encoding='utf8') as f:
        c = f.read()
        c = c.replace("{{username}}", username)
        email1 = Email(
            email, 'Bienvenue sur Eas.Ink {0}'.format(username), c
        )
        queue_email.send_mail(email1)