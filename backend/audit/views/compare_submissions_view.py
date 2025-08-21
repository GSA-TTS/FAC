from functools import partial
from django.shortcuts import render, reverse
from django.views import generic
from django.core.exceptions import PermissionDenied
from audit.compare_two_submissions import compare_report_ids
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    ACCESS_ROLES,
    Access,
    SingleAuditChecklist,
)

import logging

logger = logging.getLogger(__name__)

# {
#     "general_information": "General Information",
#     "audit_information": "Audit Information",
#     "federal_awards": "Federal Awards",
#     "corrective_action_plan": "Corrective Action Plan",
#     "findings_text": "Findings Text",
#     "findings_uniform_guidance": "Findings Uniform Guidance",
#     "additional_ueis": "Additional Ueis",
#     "additional_eins": "Additional Eins",
#     "secondary_auditors": "Secondary Auditors",
#     "notes_to_sefa": "Notes To Sefa",
#     "tribal_data_consent": "Tribal Data Consent",
# }

# For examples
# https://github.com/GSA-TTS/FAC/issues/5102#issuecomment-3065360843

# Two very similar
# http://localhost:8000/audit/compare/2023-12-GSAFAC-0000058119/2023-12-GSAFAC-0000065436
# Two completely different (not actually resubs)
# http://localhost:8000/audit/compare/2023-12-GSAFAC-0000058119/2023-09-GSAFAC-0000016690
# Here's one that is a resub, but has some interesting changes
# http://localhost:8000/audit/compare/2022-09-CENSUS-0000258487/2022-09-CENSUS-0000258486
# Ooh. Interesting. They were missing a section? Seems odd.
# http://localhost:8000/audit/compare/2023-09-GSAFAC-0000046021/2023-09-GSAFAC-0000040598

# http://localhost:8000/audit/compare/2023-03-GSAFAC-0000000881/2023-03-GSAFAC-0000007892


class CompareSubmissionsView(generic.View):

    def get(self, request, *args, **kwargs):
        report_id_1 = kwargs["report_id_1"]
        report_id_2 = kwargs["report_id_2"]

        try:
            sac_1 = SingleAuditChecklist.objects.get(report_id=report_id_1)
            sac_2 = SingleAuditChecklist.objects.get(report_id=report_id_2)
            logger.info(f"{sac_1}, {sac_2}")
            compared = compare_report_ids(sac_1, sac_2)
            context = {"comparison": compared}
            nice_names = {}
            for k in compared.keys():
                nice_names[k] = k.replace("_", " ").title()

            context = context | {"nice_names": nice_names}
            context = context | {"r1": report_id_1}
            context = context | {"r2": report_id_2}
            logger.info(context)
            return render(request, "audit/compare_submissions.html", context)
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied(
                "You do not have access to this comparison page."
            ) from err
