import json
import logging
from json import JSONDecodeError

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from store.models import KeyVal
from store.utils import reset_ttl, format_pair


logger = logging.getLogger("all")


class KeyValView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if request.method in settings.ACCEPTABLE_REQUEST_METHODS:

            if request.method in settings.SETTER_METHODS:
                # validate data
                try:
                    self.params_dict = json.loads(request.body)
                except JSONDecodeError:
                    return JsonResponse({"message": "Data missing or invalid format (only Json format is allowed)"}, status=400)

                if not self.params_dict:
                    return JsonResponse({"message": "Data missing"}, status=400)

            self.non_expired_kv_queryset = KeyVal.objects.non_expired()
            return super().dispatch(request, *args, **kwargs)

        else:
            return JsonResponse({"message": f'Method Not Allowed ({request.method})'}, status=405)

    def get(self, request):
        specified_keys = request.GET.get("keys")
        specified_key_list = [key.strip() for key in specified_keys.split(",")] if specified_keys else []

        if specified_key_list:
            reset_ttl(specified_key_list)

        data = format_pair(self.non_expired_kv_queryset, specified_key_list)
        return JsonResponse(data, status=200)

    def post(self, request):
        # return if any submitted key already exists
        if self.non_expired_kv_queryset.filter(key__in=self.params_dict.keys()).exists():
            existing_keys = list(self.non_expired_kv_queryset.filter(key__in=self.params_dict.keys()).values_list("key", flat=True))
            logger.info(f"duplicate key request for {existing_keys}")
            return JsonResponse({"message": f"Some keys are already exists.", "existing_keys": existing_keys}, status=409)

        for key, value in self.params_dict.items():
            try:
                KeyVal.objects.create(key=key, value=value)
            except Exception as e:
                logger.critical(f"key: {key}, value: {value} not created")
                logger.critical(str(e))

        reset_ttl(self.params_dict.keys())
        return JsonResponse({"message": "Values stored successfully"}, status=201)

    def patch(self, request):
        for key, value in self.params_dict.items():
            try:
                kv_obj = self.non_expired_kv_queryset.get(key=key)
                kv_obj.value = value
                kv_obj.save()
            except KeyVal.DoesNotExist:
                pass

        reset_ttl(self.params_dict.keys())
        return JsonResponse({"message": "Values updated successfully"}, status=200)
