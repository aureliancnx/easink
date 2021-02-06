import codecs
import json
import time

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from djangoProject.objects.Email import Email
from djangoProject.objects.Profile import Profile
from djangoProject.queues import queue_email
from djangoProject.utils import security_utils, password_utils


def forgot_password_request(request):
    if security_utils.rate_limited(request, 'forgot-password', 10):
        return HttpResponseBadRequest('Veuillez patienter avant chaque tentative de réinitialisation de mot de passe.')

    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not "email" in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier une adresse email.')

    email = request.POST.get('email')

    try:
        user = User.objects.filter(email=email)

        if not user.exists():
            raise Exception('Unknown email')
    except Exception as e:
        print(e)
        return HttpResponseBadRequest('Ce compte n\'existe pas. Veuillez vérifier l\'orthographe de l\'adresse email.')

    user = user.get()

    if not user.is_active:
        return HttpResponseBadRequest('Ce compte utilisateur n\'est pas actif.')

    profile = user.profile
    if len(profile.verify_token) > 0:
        return HttpResponseBadRequest('Ce compte n\'est pas encore vérifié. Veuillez vérifier le compte depuis l\'email reçu.')

    ftime = profile.forgotpassword_time
    if ftime is None:
        ftime = 0

    if ftime + (10 * 60) > time.time():
        return HttpResponseBadRequest('Une demande de réinitialisation de mot de passe a déjà été effectuée récemment. Veuillez réessayer dans dix minutes.')

    profile.forgotpassword_token = security_utils.generate_token()
    profile.forgotpassword_time = time.time()

    profile.save()

    sendemail_request(user.username, profile.forgotpassword_token, user.email)

    return HttpResponse('Une requête de réinitialisation du mot de passe a été envoyée à votre adresse email. Consultez votre boîte mail pour continuer le processus.')

def forgot_password_change(request, token):
    if security_utils.rate_limited(request, 'forgot-password-change', 10):
        return HttpResponseBadRequest('Veuillez patienter avant chaque tentative de réinitialisation de mot de passe.')

    profile = Profile.objects.filter(forgotpassword_token=token,forgotpassword_time__gt=time.time()-3600)

    if not profile.exists():
        return render(request, 'verify-error.html', {'message': 'Demande invalide ou expirée. Veuillez effectuer une nouvelle demande de changement de mot de passe.'})

    if not request.method == "POST":
        return render(request, 'change-password.html')

    if not 'password1' in request.POST or not 'password2' in request.POST:
        return render(request, 'change-password.html', {'error': 'Veuillez spécifier le nouveau mot de passe et le mot de passe de confirmation.'})

    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')

    if len(password1) < 1 or len(password2) < 1:
        return render(request, 'change-password.html', {'error': 'Veuillez spécifier le nouveau mot de passe et le mot de passe de confirmation.'})

    passwd_check = password_utils.password_check(password1)

    if passwd_check is not None:
        return render(request, 'change-password.html', {'error': passwd_check})

    if password1 != password2:
        return render(request, 'change-password.html', {'error': 'Les deux mots de passe ne sont pas identiques. Veuillez réessayer.'})

    profile = profile.get()

    profile.forgotpassword_token = ""
    profile.forgotpassword_time = -1

    profile.save()

    user = profile.user
    user.set_password(password1)
    user.save()

    sendemail_changed(user.username, user.email)

    return render(request, 'verify-success.html', {'message':'Le mot de passe a été modifié avec succès.'})


def sendemail_request(username, token, email):
    with codecs.open('mail-templates/account-forgot-password.html', 'r', encoding='utf8') as f:
        c = f.read()
        c = c.replace("{{username}}", username)
        c = c.replace("{{token}}", token)
        email1 = Email(
            email, 'Demande de réinitialisation du mot de passe', c
        )
        queue_email.send_mail(email1)

def sendemail_changed(username, email):
    with codecs.open('mail-templates/account-password-changed.html', 'r', encoding='utf8') as f:
        c = f.read()
        c = c.replace("{{username}}", username)
        email1 = Email(
            email, 'Mot de passe Eas.Ink modifié', c
        )
        queue_email.send_mail(email1)
