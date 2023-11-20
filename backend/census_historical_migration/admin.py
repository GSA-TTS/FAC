from django.contrib import admin  # noqa: F401

from census_historical_migration.models import (
    ELECAUDITHEADER,
    FAILED_SACS,
    CHANGE_RECORDS,
)

admin.site.register(ELECAUDITHEADER)
admin.site.register(FAILED_SACS)
admin.site.register(CHANGE_RECORDS)
