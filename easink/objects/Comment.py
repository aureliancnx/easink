from django.db import models


class Comment(models.Model):
    artist_id = models.CharField(max_length=255)
    author_id = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    status = models.IntegerField(max_length=255)
    date = models.CharField(max_length=255)
    time = models.IntegerField(max_length=255)