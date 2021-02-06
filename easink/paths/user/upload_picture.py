import os
from datetime import time

from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseBadRequest

from djangoProject import settings
from djangoProject.objects.Profile import Profile


def upload(request):
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

    if not 'profile-picture' in request.FILES:
        return HttpResponseBadRequest('Veuillez téléverser une image.')

    picture = request.FILES['profile-picture']

    picture_path = 'profile-picture/{0}.png'.format(user.profile.unique_id)
    picture_path_full = os.path.join(settings.MEDIA_ROOT, picture_path)

    if os.path.exists(picture_path_full):
        os.remove('media/{0}'.format(picture_path_full))

    path = default_storage.save(picture_path, ContentFile(picture.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)

    try:
        trial_image = Image.open(picture_path_full)
        trial_image.verify()
        v = trial_image
        b = Image.MIME.get(trial_image.format)
    except:
        return HttpResponseBadRequest('L\'image de profil n\'est pas une image valide. Veuillez réessayer.')

    profile.profile_img = '{0}{1}'.format(settings.MEDIA_URL, picture_path_full)
    profile.save()