import codecs
import uuid
from pathlib import Path
from time import sleep

import stdnum
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse
from email_validator import EmailNotValidError, validate_email
from stdnum.fr import siret

from djangoProject.objects.Email import Email
from djangoProject.objects.Profile import Profile
from djangoProject.queues import queue_email
from djangoProject.utils import password_utils, security_utils


# TODO COMMENTS


def register(request):
    if security_utils.rate_limited(request, 'register', 30):
        return HttpResponseBadRequest('Veuillez patienter avant chaque tentative d\'inscription.')

    if request.user.is_authenticated:
        return HttpResponseBadRequest('Vous êtes déjà connecté.')

    if not request.method == "POST":
        return HttpResponseBadRequest('Invalid method.')

    if not "type" in request.POST:
        return HttpResponseBadRequest('Vous devez spécifier le type d\'inscription.')

    type = request.POST.get("type")

    if type == "TATTOIST":
        return register_tattoist(request)

    if type == "CLIENT":
        return register_client(request)

    return HttpResponseBadRequest('Le type d\'inscription est invalide.')


def register_basic(request, tattoist):

    if not 'email' in request.POST:
        return HttpResponseBadRequest("Veuillez préciser votre adresse email.")

    if not 'username' in request.POST:
        return HttpResponseBadRequest("Veuillez préciser votre nom d'utilisateur.")

    if not 'password' in request.POST:
        return HttpResponseBadRequest("Veuillez préciser votre mot de passe.")

    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")

    email = email.lstrip()
    email = email.lower()

    try:
        # Check if the username already exists
        user = User.objects.filter(username=username)

        if user.exists():
            if tattoist:
                return HttpResponseBadRequest('Ce nom d\'artiste est déjà pris.')

            return HttpResponseBadRequest('Ce nom d\'utilisateur est déjà pris.')

        # Check if the email address already exists
        user = User.objects.filter(email=email)

        if user.exists():
            return HttpResponseBadRequest('Cette adresse email est déjà utilisée.')

        password_check = password_utils.password_check(password)

        if not password_check is None:
            return HttpResponseBadRequest(password_check)

        try:
            valid = validate_email(email)
        except EmailNotValidError as e:
            return HttpResponseBadRequest('Adresse email invalide.')

    except Exception as e:
        return HttpResponseBadRequest('Erreur lors de l\'inscription.')

    return None


def register_tattoist(request):
    basic_check = register_basic(request, False)

    if basic_check is not None:
        return basic_check

    if not "shop_name" in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier le nom du shop.')

    if not "shop_siret" in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier le numéro de SIRET.')

    if not "shop_localization" in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier l\'adresse de localisation.')

    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    shop_name = request.POST.get("shop_name")
    shop_siret = request.POST.get("shop_siret")
    shop_localization = request.POST.get("shop_localization")
    shop_email = ""
    shop_phone = ""

    if len(shop_name) < 4 or len(shop_name) > 100:
        return HttpResponseBadRequest('Le nom du shop doit faire entre 4 et 100 caractères.')

    if len(shop_siret) < 4 or len(shop_siret) > 100:
        return HttpResponseBadRequest('Le SIRET est invalide.')

    try:
        siret.validate(shop_siret)
    except:
        return HttpResponseBadRequest('Le numéro de SIRET est invalide.')

    if len(shop_localization) < 4 or len(shop_localization) > 100:
        return HttpResponseBadRequest('La localisation de la boutique doit faire entre 4 et 100 caractères.')

    if "shop_email" in request.POST:
       shop_email = request.POST.get("shop_email")
       try:
           valid = validate_email(email)
       except EmailNotValidError as e:
           return HttpResponseBadRequest('Adresse email de contact invalide.')

    if shop_phone in request.POST:
        shop_phone = request.POST.get("shop_phone")
        if not shop_phone.isdecimal():
            return HttpResponseBadRequest('Le numéro de téléphone de contact est invalide.')

        if len(shop_phone) != 10:
            return HttpResponseBadRequest('Le numéro de téléphone de contact doit contenir dix chiffres.')

    email = email.lstrip()
    email = email.lower()

    try:
        user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)

        profile = Profile(type="TATTOIST")

        found_uniqueid = False

        while not found_uniqueid:
            unique_id = str(uuid.uuid4())
            profile_exists = Profile.objects.filter(unique_id=unique_id)

            if not profile_exists.exists():
                profile.unique_id = unique_id
                found_uniqueid = True
            else:
                sleep(0.2)

        profile.verify_token = security_utils.generate_token()
        profile.shop_name = shop_name
        profile.shop_siret = shop_siret
        profile.shop_localization = shop_localization
        profile.shop_email = shop_email
        profile.shop_phone = shop_phone

        user.profile = profile
        profile.save()

        send_verify_email(username, email, profile.verify_token)
        ga_register()

        return HttpResponse('Votre compte a été créé. Vous avez un reçu un email de confirmation afin de valider votre compte.')

    except Exception as e:
        print(e)
        return HttpResponseBadRequest('Une erreur est survenue lors de l\'inscription')


def register_client(request):
    basic_check = register_basic(request, False)

    if basic_check is not None:
        return basic_check

    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")

    email = email.lstrip()
    email = email.lower()

    try:
        user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)

        print('register: "{0}"'.format(password))
        user.set_password(password)

        profile = Profile(type="CLIENT")
        found_uniqueid = False

        while not found_uniqueid:
            unique_id = str(uuid.uuid4())
            profile_exists = Profile.objects.filter(unique_id=unique_id)

            if not profile_exists.exists():
                profile.unique_id = unique_id
                found_uniqueid = True
            else:
                sleep(0.2)

        profile.verify_token = security_utils.generate_token()

        user.profile = profile
        profile.save()
        user.save()

        send_verify_email(username, email, profile.verify_token)
        ga_register()

        return HttpResponse('Votre compte a été créé. Vous avez un reçu un email de confirmation afin de valider votre compte.')

    except Exception as e:
        print(e)
        return HttpResponseBadRequest('Une erreur est survenue lors de l\'inscription')


def ga_register():
    # TODO Add Google Analytics register info
    return None


def send_verify_email(username, email, token):
    with codecs.open('mail-templates/account-verify.html', 'r', encoding='utf8') as f:
        c = f.read()
        c = c.replace("{{username}}", username)
        c = c.replace("{{token}}", token)
        email1 = Email(
            email, 'Vérifiez votre adresse email Eas.Ink', c
        )
        queue_email.send_mail(email1)