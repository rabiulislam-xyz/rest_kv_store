from django.test import TestCase

from store.models import KeyVal


class GetKeyValueTest(TestCase):
    def setUp(self):
        self.kv_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
        for k, v in self.kv_dict.items():
            KeyVal.objects.create(key=k, value=v)

    def test_get_all_key_values(self):
        response = self.client.get("/values")
        self.assertEqual(response.json(), self.kv_dict)
        self.assertEqual(response.status_code, 200)

    def test_get_single_key_value(self):
        response = self.client.get("/values?keys=key1,key2")
        self.assertEqual(response.json(), self.kv_dict)
        self.assertEqual(response.status_code, 200)
