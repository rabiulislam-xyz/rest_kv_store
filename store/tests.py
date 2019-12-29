from django.test import TestCase

from store.models import KeyVal


class TestKeyValue(TestCase):
    @classmethod
    def setUpTestData(cls):
        KeyVal.objects.create(key="key1", value="value1")
        KeyVal.objects.create(key="key2", value="value2")
        KeyVal.objects.create(key="key3", value="value3")

    def test_get_all_key_values(self):
        response = self.client.get("/values", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "value1", "key2": "value2", "key3": "value3"})
        self.assertEqual(response.status_code, 200)

    def test_get_single_valid_key_value(self):
        response = self.client.get("/values?keys=key1", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "value1"})
        self.assertEqual(response.status_code, 200)

    def test_get_single_invalid_key_value(self):
        response = self.client.get("/values?keys=invalid1", content_type='application/json')
        self.assertEqual(response.json(), {"invalid1": None})
        self.assertEqual(response.status_code, 200)

    def test_get_multiple_valid_key_values(self):
        response = self.client.get("/values?keys=key1,key2", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "value1", "key2": "value2"})
        self.assertEqual(response.status_code, 200)

    def test_get_multiple_valid_and_invalid_key_values(self):
        response = self.client.get("/values?keys=key1,key2,invalid1,invalid2", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "value1", "key2": "value2", "invalid1": None, "invalid2": None})
        self.assertEqual(response.status_code, 200)

    def test_create_new_single_key_value(self):
        response = self.client.post("/values", content_type='application/json', data={"newKey": "newValue"})
        self.assertEqual(response.status_code, 201)

    def test_create_new_multiple_key_values(self):
        response = self.client.post("/values", content_type='application/json', data={"newKey1": "newValue1", "newKey2": "newValue2"})
        self.assertEqual(response.json(), {'message': 'Values stored successfully'})
        self.assertEqual(response.status_code, 201)

    def test_create_existing_single_key_value(self):
        response = self.client.post("/values", content_type='application/json', data={"key1": "value1"})
        self.assertEqual(response.json(), {'message':  "Some keys are already exists.", "existing_keys": ["key1"]})
        self.assertEqual(response.status_code, 409)

    def test_create_existing_multiple_key_values(self):
        response = self.client.post("/values", content_type='application/json', data={"key1": "value1", "key2": "value2"})
        self.assertEqual(response.json(), {'message':  "Some keys are already exists.", "existing_keys": ["key1", "key2"]})
        self.assertEqual(response.status_code, 409)

    def test_update_single_key_value(self):
        response = self.client.get("/values?keys=key1", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "value1"})

        response = self.client.patch("/values", content_type='application/json', data={"key1": "newValue1"})
        self.assertEqual(response.json(), {'message': 'Values updated successfully'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/values?keys=key1", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "newValue1"})

    def test_update_multiple_key_values(self):
        response = self.client.get("/values?keys=key1,key2", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "value1", "key2": "value2"})

        response = self.client.patch("/values", content_type='application/json', data={"key1": "newValue1", "key2": "newValue2"})
        self.assertEqual(response.json(), {'message': 'Values updated successfully'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/values?keys=key1,key2", content_type='application/json')
        self.assertEqual(response.json(), {"key1": "newValue1", "key2": "newValue2"})

    def test_update_invalid_single_key_value(self):
        response = self.client.patch("/values", content_type='application/json', data={"invalidKey": "invalidValue"})
        self.assertEqual(response.json(), {'message': 'Values updated successfully'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/values?keys=invalidKey", content_type='application/json')
        self.assertEqual(response.json(), {"invalidKey": None})
