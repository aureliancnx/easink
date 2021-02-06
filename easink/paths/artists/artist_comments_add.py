# TODO comments
import collections
import time
from datetime import datetime

from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

# TODO comments
from djangoProject.objects.Comment import Comment
from djangoProject.objects.Profile import Profile
from djangoProject.queues import artists_manager
from djangoProject.utils import math_utils, security_utils


def artist_add_comments(request):
    if security_utils.rate_limited(request, 'add-comment', 10):
        return HttpResponseBadRequest('Veuillez patienter avant chaque tentative d\'ajout de commentaire.')

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
        artp = artists_manager.artists[artist]
        if artp.unique_id == uuid:
            art = artp
            break

    if art is None:
        return HttpResponseBadRequest('Artiste inconnu.')

    artist_id = art.unique_id
    author_id = profile.unique_id
    timestamp = time.time()
    date = datetime.today().strftime('%d/%m/%Y %H:%M:%S')

    if not 'message' in request.POST:
        return HttpResponseBadRequest('Veuillez spécifier le message.')

    message = request.POST.get('message')

    if len(message) < 1:
        return HttpResponseBadRequest('Votre message ne peut pas être vide.')

    if len(message) > 250:
        return HttpResponseBadRequest('Le commentaire ne peut pas excéder 250 caractères.')

    comment_exist = Comment.objects.filter(artist_id=artist_id,author_id=author_id)

    if comment_exist.exists():
        return HttpResponseBadRequest('Vous avez déjà écrit un commentaire pour cet artiste.')

    comment = Comment.objects.create(artist_id=artist_id, author_id=author_id, time=timestamp,
                                     message=message, date=date, status=0)

    return HttpResponse('Votre commentaire a été pris en compte. Il sera publié sous peu de temps.')