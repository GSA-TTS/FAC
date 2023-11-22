from django.contrib import admin  # noqa: F401

from census_historical_migration.models import (
    ELECAUDITHEADER,
    ReportMigrationStatus,
    MigrationErrorDetail,
)

admin.site.register(ELECAUDITHEADER)
admin.site.register(ReportMigrationStatus)
admin.site.register(MigrationErrorDetail)
