from django.contrib import admin

from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
    OneTimeAccess,
)

admin.site.register(AdditionalEin)
admin.site.register(AdditionalUei)
admin.site.register(CapText)
admin.site.register(FederalAward)
admin.site.register(Finding)
admin.site.register(FindingText)
admin.site.register(General)
admin.site.register(Note)
admin.site.register(Passthrough)
admin.site.register(SecondaryAuditor)
admin.site.register(OneTimeAccess)
