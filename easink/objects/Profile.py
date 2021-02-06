from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    verify_token = models.CharField(max_length=255)
    log_token = models.CharField(max_length=255)
    log_expire = models.IntegerField(max_length=255)
    shop_name = models.CharField(max_length=255)
    shop_siret = models.CharField(max_length=255)
    shop_localization = models.CharField(max_length=255)
    shop_email = models.CharField(max_length=255)
    shop_phone = models.CharField(max_length=255)
    shop_styles = models.CharField(max_length=255)
    shop_bio = models.CharField(max_length=255)
    shop_long = models.CharField(max_length=255)
    shop_lat = models.CharField(max_length=255)
    social_facebook = models.CharField(max_length=255)
    social_instagram = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    forgotpassword_token = models.CharField(max_length=255)
    forgotpassword_time = models.IntegerField(max_length=255)
    profile_img = models.CharField(max_length=255)