import datetime

from celery import shared_task

from store.models import KeyVal


@shared_task
def remove_expired_keys():
    print(f"removing expired keys at: {datetime.datetime.now()}!")
    count = KeyVal.objects.expired().count()
    KeyVal.objects.expired().delete()
    print(f"removed {count} expired keys")
