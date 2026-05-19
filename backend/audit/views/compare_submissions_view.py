from django.shortcuts import render
from django.views import generic
from django.core.exceptions import PermissionDenied
from audit.viewlib.compare_two_submissions import compare_with_prev
from audit.models import (
    SingleAuditChecklist,
    Access,
)
from audit.mixins import (
    LoginRequiredMixin,
)
from users.models import UserPermission


import logging

logger = logging.getLogger(__name__)


class CompareSubmissionsView(LoginRequiredMixin, generic.View):

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        current_user = request.user

        try:
            sac_1 = SingleAuditChecklist.objects.get(report_id=report_id)
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied(f"Cannot find report id {report_id}") from err

        # First, find out if we should bother.
        # FIXME: Can we pass more information back? The 403 does not answer "why."
        # We will accept the "next" audit, because compare_with_prev can figure out
        # which audit to compare to which, in order to be more forgiving.
        if sac_1.resubmission_meta is None or (
            "previous_report_id" not in sac_1.resubmission_meta
            and "next_report_id" not in sac_1.resubmission_meta
        ):
            raise PermissionDenied(
                "The audit provided does not have any associated audits to compare with."
            )

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
            logger.debug("Authenticated as a user on the audit")
            pass
        # If I am a Federal user, I can see the diff
        elif is_authenticated and is_federal_user:
            logger.debug("Authenticated as a federal user")
            pass
        else:
            raise PermissionDenied("You do not have access to this comparison page.")

        # We get here if we passed one of the above conditions.
        report_id_1, report_id_2, compared = compare_with_prev(sac_1)
        context = {"comparison": compared}

        nice_names = {}
        for k in compared.keys():
            nice_names[k] = k.replace("_", " ").title()

        # does our SACs have any differences ?
        has_diffs = False
        for val in compared.values():
            if val["status"] != "same":
                has_diffs = True
                break

        context = context | {"has_diffs": has_diffs}
        context = context | {"nice_names": nice_names}
        context = context | {"r1": report_id_1}
        context = context | {"r2": report_id_2}

        return render(request, "audit/compare_submissions.html", context)
