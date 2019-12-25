from rest_framework import serializers

from store.models import KeyVal


class KeyValSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyVal
        fields = ['key', 'value']
