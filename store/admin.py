from django.contrib import admin

from store.models import KeyVal


@admin.register(KeyVal)
class KeyValAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'created_at', 'updated_at')
    search_fields = ('key', 'value')
