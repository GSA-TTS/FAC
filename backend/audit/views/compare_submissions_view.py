from django.shortcuts import render
from django.views import generic
from django.core.exceptions import PermissionDenied
from audit.compare_two_submissions import compare_with_prev
from audit.models import (
    SingleAuditChecklist,
    ACCESS_ROLES,
    Access,
)
from audit.mixins import (
    LoginRequiredMixin,
)
from users.models import Permission, UserPermission


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


# http://localhost:8000/audit/compare/2023-06-GSAFAC-0000000697
# http://localhost:8000/audit/compare/2023-06-GSAFAC-0000002166
# http://localhost:8000/audit/compare/2022-12-GSAFAC-0000001787
# http://localhost:8000/audit/compare/2023-06-GSAFAC-0000002901
# http://localhost:8000/audit/compare/2023-06-GSAFAC-0000013043
# http://localhost:8000/audit/compare/2023-06-GSAFAC-0000005147
# http://localhost:8000/audit/compare/2023-06-GSAFAC-0000001699
# http://localhost:8000/audit/compare/2022-12-GSAFAC-0000007921

# The mixin should require that we can see the first report.
# We have to check the second.


def _get_friendly_role(role):
    return dict(ACCESS_ROLES)[role]


def _user_entry(access: Access) -> dict:
    """Given an Access, return a dict of relevant info."""
    return {
        "name": access.fullname,
        "email": access.email,
        "role": _get_friendly_role(access.role),
        "user_exists": bool(access.user),
        "never_logged_in_flag": "" if bool(access.user) else "*",
        "id": access.id,
    }


# The access control we're implementing:
# IF the status == `DISSEMINATED` and I'm logged in as a Federal user
# THEN I can see both reports
#
# IF the status == `IN_PROGRESS` and I own the first report
# THEN I can see both reports

# Does it matter if the audit is done?
# Should I be allowed to see the differences for all time?


class CompareSubmissionsView(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        report_id_1 = kwargs["report_id_1"]
        current_user = request.user
        try:
            sac_1 = SingleAuditChecklist.objects.get(report_id=report_id_1)

            # First, find out if we should bother.
            # FIXME: Can we pass more information back? The 403 does not answer "why."
            if sac_1.resubmission_meta is None:
                raise PermissionDenied("There is no prior submission for this audit.")
            # We will accept the "next" audit, because compare_with_prev can figure out
            # which audit to compare to which, in order to be more forgiving.
            if (
                "previous_report_id" not in sac_1.resubmission_meta
                and "next_report_id" not in sac_1.resubmission_meta
            ):
                raise PermissionDenied("There is nothing to compare this audit with.")

            #############################################
            # We are doing the permissions checking here instead of a mixin.
            # Why? Becuase we do not have conditional mixins.
            # To start, you must be logged in.
            #
            # Once logged in, all
            # federal users can see all differences.
            #
            # For all other users, they must be associated with the audit.
            # Get the accesses for this SAC

            accesses = Access.objects.filter(sac=sac_1)
            user_ids_on_audit = list(map(lambda acc: acc.user_id, accesses))

            is_authenticated = current_user.is_authenticated
            is_on_audit = current_user.id in user_ids_on_audit
            is_federal_user = UserPermission.objects.filter(
                user_id=current_user.id
            ).exists()

            logger.info(
                f"[DIFF] {current_user.id} {sac_1.report_id} {is_authenticated} AND ({is_on_audit} OR {is_federal_user})"
            )

            # If I am attached to this report, I can see the diff.
            if is_authenticated and is_on_audit:
                pass
            # If I am a Federal user, I can see the diff
            elif is_authenticated and is_federal_user:
                pass
            else:
                raise PermissionDenied(
                    "You do not have access to this comparison page."
                )

            # We get here if we passed one of the above conditions.
            report_id_1, report_id_2, compared = compare_with_prev(sac_1)
            context = {"comparison": compared}
            nice_names = {}
            for k in compared.keys():
                nice_names[k] = k.replace("_", " ").title()

            context = context | {"nice_names": nice_names}
            context = context | {"r1": report_id_1}
            context = context | {"r2": report_id_2}

            print(context)

            return render(request, "audit/compare_submissions.html", context)
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied(
                "You do not have access to this comparison page."
            ) from err
