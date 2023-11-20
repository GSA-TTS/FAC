from django.contrib import admin  # noqa: F401

from census_historical_migration.models import (
    ELECAUDITHEADER,
    FailedSacs,
    ChangeRecords,
)

admin.site.register(ELECAUDITHEADER)
admin.site.register(FailedSacs)
admin.site.register(ChangeRecords)
