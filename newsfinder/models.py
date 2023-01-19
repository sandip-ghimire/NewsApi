from django.db import models
from django.utils import timezone


class News(models.Model):
    title = models.CharField(max_length=500, default=None, blank=True, null=True)
    content = models.CharField(max_length=100000, default=None, blank=True, null=True)
    word_count = models.IntegerField(default=0)
    url = models.CharField(max_length=300)
    channel = models.ForeignKey('Channel', default=None, blank=True, null=True, on_delete=models.SET_DEFAULT)
    source = models.CharField(max_length=100, default=None, blank=True, null=True)
    published_date = models.DateTimeField(default=None, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.url


class Channel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
