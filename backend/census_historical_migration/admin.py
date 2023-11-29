from django.contrib import admin  # noqa: F401

from census_historical_migration.models import (
    ELECAUDITHEADER,
    ELECEINS,
    ELECAUDITFINDINGS,
    ELECNOTES,
    ELECFINDINGSTEXT,
    ELECCPAS,
    ELECAUDITS,
    ELECPASSTHROUGH,
    ELECUEIS,
    ELECCAPTEXT,
    ReportMigrationStatus,
    MigrationErrorDetail,
)

admin.site.register(ELECAUDITHEADER)
admin.site.register(ELECEINS)
admin.site.register(ELECAUDITFINDINGS)
admin.site.register(ELECNOTES)
admin.site.register(ELECFINDINGSTEXT)
admin.site.register(ELECCPAS)
admin.site.register(ELECAUDITS)
admin.site.register(ELECPASSTHROUGH)
admin.site.register(ELECUEIS)
admin.site.register(ELECCAPTEXT)
admin.site.register(ReportMigrationStatus)
admin.site.register(MigrationErrorDetail)
