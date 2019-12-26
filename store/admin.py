from django.contrib import admin
from django.utils import timezone

from store.models import KeyVal


@admin.register(KeyVal)
class KeyValAdmin(admin.ModelAdmin):
    def is_valid(self, obj):
        return obj.ttl >= timezone.localtime()
    is_valid.boolean = True
    is_valid.short_description = "Is valid (not expired)"

    list_display = ('key', 'value', 'ttl', 'is_valid')
    search_fields = ('key', 'value')

