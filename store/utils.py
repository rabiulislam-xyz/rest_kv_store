import datetime
import logging

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from store.models import KeyVal

logger = logging.getLogger('all')


def format_pair(non_expired_kv_queryset: QuerySet, specified_keys: list = None) -> dict:
    """
    This function take a queryset and convert into key:val pair dictionary.
    set values of specified keys as None which are not in queryset.
    """
    result = {i['key']: i['value'] for i in non_expired_kv_queryset.values("key", "value")}

    # reformat result as per specified keys
    if specified_keys and specified_keys != list(result.keys()):
        temp_result = {}
        for key in specified_keys:
            temp_result[key] = result.get(key, None)
        result = temp_result

    return result


def reset_ttl(keys: list) -> None:
    logger.info(f"updating TTL for keys: {keys}")
    KeyVal.objects.filter(key__in=keys).update(ttl=timezone.localtime() + datetime.timedelta(seconds=settings.DEFAULT_TTL))

