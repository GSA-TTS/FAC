from django.contrib import admin
from dissemination.models import (
    TribalApiAccessKeyIds,
)
import datetime


class TribalApiAccessKeyIdsAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "key_id",
        "date_added",
    )

    search_fields = (
        "email",
        "key_id",
    )

    fields = [
        "email",
        "key_id",
    ]

    def save_model(self, request, obj, form, change):
        obj.email = obj.email.lower()
        obj.date_added = datetime.date.today()
        super().save_model(request, obj, form, change)


admin.site.register(TribalApiAccessKeyIds, TribalApiAccessKeyIdsAdmin)
