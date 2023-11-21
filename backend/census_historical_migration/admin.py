from django.contrib import admin  # noqa: F401

from census_historical_migration.models import (
    ELECAUDITHEADER,
    ReportMigrationStatus,
)

admin.site.register(ELECAUDITHEADER)
admin.site.register(ReportMigrationStatus)
