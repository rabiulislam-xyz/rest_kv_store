from django.db.models import QuerySet

from store.models import KeyVal


def format_pair(queryset: QuerySet, specified_keys: list = None) -> dict:
    """
    This function take a queryset and convert into key:val pair dictionary.
    set values of specified keys as None which are not in queryset.
    """
    result = {i['key']: i['value'] for i in queryset.values("key", "value")}

    if specified_keys and len(specified_keys) != len(result.keys()):
        for key in set(specified_keys).difference(set(result.keys())):
            result[key] = None
    return result


def update_values(kv_pair_dict: dict, create_if_not_exists: bool = False) -> QuerySet:

    for key, value in kv_pair_dict.items():
        try:
            kv_obj = KeyVal.objects.get(key=key)
            kv_obj.value = value
            kv_obj.save()
        except KeyVal.DoesNotExist:
            if create_if_not_exists:
                KeyVal.objects.create(key=key, value=value)

    return KeyVal.objects.filter(key__in=kv_pair_dict.keys())


def reset_ttl(queryset: QuerySet) -> None:
    print("resetting ttl for : ")
    print(queryset)

