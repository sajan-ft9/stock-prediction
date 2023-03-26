from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    link = models.CharField(max_length=255)