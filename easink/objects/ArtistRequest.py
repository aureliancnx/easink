from django.db import models


class ArtistRequest(models.Model):
    author = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    shop_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    instagram = models.CharField(max_length=255)