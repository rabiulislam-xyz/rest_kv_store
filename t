[1mdiff --git a/store/tests.py b/store/tests.py[m
[1mindex f8aeb3f..0e2d84a 100644[m
[1m--- a/store/tests.py[m
[1m+++ b/store/tests.py[m
[36m@@ -46,13 +46,13 @@[m [mclass TestKeyValue(TestCase):[m
 [m
     def test_create_existing_single_key_value(self):[m
         response = self.client.post("/values", content_type='application/json', data={"key1": "value1"})[m
[31m-        self.assertEqual(response.json(), {'message': 'Values stored successfully'})[m
[31m-        self.assertEqual(response.status_code, 201)[m
[32m+[m[32m        self.assertEqual(response.json(), {'message':  "Some keys are already exists.", "existing_keys": ["key1"]})[m
[32m+[m[32m        self.assertEqual(response.status_code, 409)[m
 [m
     def test_create_existing_multiple_key_values(self):[m
         response = self.client.post("/values", content_type='application/json', data={"key1": "value1", "key2": "value2"})[m
[31m-        self.assertEqual(response.json(), {'message': 'Values stored successfully'})[m
[31m-        self.assertEqual(response.status_code, 201)[m
[32m+[m[32m        self.assertEqual(response.json(), {'message':  "Some keys are already exists.", "existing_keys": ["key1", "key2"]})[m
[32m+[m[32m        self.assertEqual(response.status_code, 409)[m
 [m
     def test_update_single_key_value(self):[m
         response = self.client.get("/values?keys=key1", content_type='application/json')[m
[1mdiff --git a/store/utils.py b/store/utils.py[m
[1mindex 5d59ac6..16921e8 100644[m
[1m--- a/store/utils.py[m
[1m+++ b/store/utils.py[m
[36m@@ -1,23 +1,40 @@[m
 import datetime[m
[32m+[m[32mimport logging[m
 [m
 from django.conf import settings[m
 from django.db.models import QuerySet[m
 from django.utils import timezone[m
 [m
[32m+[m[32mfrom store.models import KeyVal[m
 [m
[31m-def format_pair(queryset: QuerySet, specified_keys: list = None) -> dict:[m
[32m+[m[32mlogger = logging.getLogger('all')[m
[32m+[m
[32m+[m
[32m+[m[32mdef format_pair(non_expired_kv_queryset: QuerySet, specified_keys: list = None) -> dict:[m
     """[m
     This function take a queryset and convert into key:val pair dictionary.[m
     set values of specified keys as None which are not in queryset.[m
     """[m
[31m-    result = {i['key']: i['value'] for i in queryset.values("key", "value")}[m
[32m+[m[32m    result = {i['key']: i['value'] for i in non_expired_kv_queryset.values("key", "value")}[m
[32m+[m[32m    print(result)[m
[32m+[m[32m    print(specified_keys)[m
[32m+[m[32m    print(len(specified_keys) != len(result.keys()))[m
[32m+[m[32m    print(specified_keys != list(result.keys()))[m
[32m+[m[32m    print(len(specified_keys), len(result.keys()))[m
[32m+[m[32m    print(set(specified_keys).difference(set(result.keys())))[m
[32m+[m
[32m+[m[32m    if specified_keys and specified_keys != list(result.keys()):[m
[32m+[m[32m        # reformat result as per specified keys[m
[32m+[m[32m        temp_result = {}[m
[32m+[m[32m        for key in specified_keys:[m
[32m+[m[32m            temp_result[key] = result.get(key, None)[m
[32m+[m[32m        result = temp_result[m
 [m
[31m-    if specified_keys and len(specified_keys) != len(result.keys()):[m
[31m-        for key in set(specified_keys).difference(set(result.keys())):[m
[31m-            result[key] = None[m
[32m+[m[32m    print(result)[m
     return result[m
 [m
 [m
[31m-def reset_ttl(queryset: QuerySet) -> None:[m
[31m-    queryset.update(ttl=timezone.localtime() + datetime.timedelta(seconds=settings.DEFAULT_TTL))[m
[32m+[m[32mdef reset_ttl(keys: list) -> None:[m
[32m+[m[32m    logger.info(f"updating TTL for keys: {keys}")[m
[32m+[m[32m    KeyVal.objects.filter(key__in=keys).update(ttl=timezone.localtime() + datetime.timedelta(seconds=settings.DEFAULT_TTL))[m
 [m
[1mdiff --git a/store/views.py b/store/views.py[m
[1mindex d044fb5..2b07b0f 100644[m
[1m--- a/store/views.py[m
[1m+++ b/store/views.py[m
[36m@@ -1,4 +1,5 @@[m
 import json[m
[32m+[m[32mimport logging[m
 from json import JSONDecodeError[m
 [m
 from django.conf import settings[m
[36m@@ -10,6 +11,9 @@[m [mfrom store.models import KeyVal[m
 from store.utils import reset_ttl, format_pair[m
 [m
 [m
[32m+[m[32mlogger = logging.getLogger("all")[m
[32m+[m
[32m+[m
 class KeyValView(View):[m
     @csrf_exempt[m
     def dispatch(self, request, *args, **kwargs):[m
[36m@@ -25,46 +29,47 @@[m [mclass KeyValView(View):[m
                 if not self.params_dict:[m
                     return JsonResponse({"message": "Data missing"}, status=400)[m
 [m
[32m+[m[32m            self.non_expired_kv_queryset = KeyVal.objects.non_expired()[m
             return super().dispatch(request, *args, **kwargs)[m
 [m
         else:[m
             return JsonResponse({"message": f'Method Not Allowed ({request.method})'}, status=405)[m
 [m
     def get(self, request):[m
[31m-        # kv_queryset = KeyVal.objects.all()[m
[31m-        kv_queryset = KeyVal.objects.non_expired()[m
         specified_keys = request.GET.get("keys")[m
         specified_key_list = [key.strip() for key in specified_keys.split(",")] if specified_keys else [][m
 [m
         if specified_key_list:[m
[31m-            kv_queryset = kv_queryset.filter(key__in=specified_key_list)[m
[31m-            reset_ttl(kv_queryset)[m
[32m+[m[32m            reset_ttl(specified_key_list)[m
 [m
[31m-        data = format_pair(kv_queryset, specified_key_list)[m
[32m+[m[32m        data = format_pair(self.non_expired_kv_queryset, specified_key_list)[m
         return JsonResponse(data, status=200)[m
 [m
     def post(self, request):[m
[31m-        kv_queryset = KeyVal.objects.all()[m
[32m+[m[32m        # return if any submitted key already exists[m
[32m+[m[32m        if self.non_expired_kv_queryset.filter(key__in=self.params_dict.keys()).exists():[m
[32m+[m[32m            existing_keys = list(self.non_expired_kv_queryset.filter(key__in=self.params_dict.keys()).values_list("key", flat=True))[m
[32m+[m[32m            logger.info(f"duplicate key request for {existing_keys}")[m
[32m+[m[32m            return JsonResponse({"message": f"Some keys are already exists.", "existing_keys": existing_keys}, status=409)[m
[32m+[m
         for key, value in self.params_dict.items():[m
             try:[m
[31m-                kv_obj = kv_queryset.get(key=key)[m
[31m-                kv_obj.value = value[m
[31m-                kv_obj.save()[m
[31m-            except KeyVal.DoesNotExist:[m
                 KeyVal.objects.create(key=key, value=value)[m
[32m+[m[32m            except Exception as e:[m
[32m+[m[32m                logger.critical(f"key: {key}, value: {value} not created")[m
[32m+[m[32m                logger.critical(str(e))[m
 [m
[31m-        reset_ttl(kv_queryset.filter(key__in= self.params_dict.keys()))[m
[32m+[m[32m        reset_ttl(self.params_dict.keys())[m
         return JsonResponse({"message": "Values stored successfully"}, status=201)[m
 [m
     def patch(self, request):[m
[31m-        non_expired_kv_queryset = KeyVal.objects.non_expired()[m
         for key, value in self.params_dict.items():[m
             try:[m
[31m-                kv_obj = non_expired_kv_queryset.get(key=key)[m
[32m+[m[32m                kv_obj = self.non_expired_kv_queryset.get(key=key)[m
                 kv_obj.value = value[m
                 kv_obj.save()[m
             except KeyVal.DoesNotExist:[m
                 pass[m
 [m
[31m-        reset_ttl(non_expired_kv_queryset.filter(key__in= self.params_dict.keys()))[m
[32m+[m[32m        reset_ttl(self.params_dict.keys())[m
         return JsonResponse({"message": "Values updated successfully"}, status=200)[m
