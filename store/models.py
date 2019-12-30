import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


def get_ttl_for_new_object():
    return timezone.now() + datetime.timedelta(seconds=settings.DEFAULT_TTL)


class KeyValManager(models.Manager):
    def non_expired(self):
        return self.filter(ttl__gte=timezone.now())

    def expired(self):
        return self.filter(ttl__lt=timezone.now())


class KeyVal(models.Model):
    key = models.TextField(unique=True, db_index=True)
    value = models.TextField()
    ttl = models.DateTimeField(default=get_ttl_for_new_object)

    objects = KeyValManager()

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        db_table = "key_values"
        verbose_name = "Key Value"
        verbose_name_plural = "KeyValues"
