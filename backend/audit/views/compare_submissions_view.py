from django.shortcuts import render
from django.views import generic
from django.core.exceptions import PermissionDenied

from audit.viewlib.compare_two_submissions import compare_with_prev
from audit.models import (
    SingleAuditChecklist,
    Access,
)

from audit.models.constants import STATUS
from users.models import UserPermission


import logging

logger = logging.getLogger(__name__)


class CompareSubmissionsView(generic.View):

    def get(self, request, report_id, route):
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
        # in both flows below:
        # - federal or users associated w/audit:
        #   - can see all comparisons
        #
        # in submission flow:
        # - un/authenticated:
        #   - have no access
        #
        # in search flow:
        # - un/authenticated:
        #   - can see comparisons that are either resubmitted or disseminated

        # Get the accesses for this SAC

        accesses = Access.objects.filter(sac=sac_1)
        user_ids_on_audit = list(map(lambda acc: acc.user_id, accesses))

        is_authenticated = current_user.is_authenticated
        is_on_audit = current_user.id in user_ids_on_audit
        is_federal_user = UserPermission.objects.filter(
            user_id=current_user.id
        ).exists()

        has_access = is_authenticated and (is_on_audit or is_federal_user)

        statuses = [STATUS.DISSEMINATED, STATUS.RESUBMITTED]

        if route == "submission" and not has_access:
            raise PermissionDenied(
                "You do not have access to this submission comparison page."
            )

        if route == "search":
            if has_access or sac_1.submission_status in statuses:
                pass
            else:
                raise PermissionDenied(
                    "You do not have access to this search comparison page."
                )

        context = _compare_sac(sac_1)
        context = context | {"is_authenticated": is_authenticated}
        context = context | {"is_on_audit": is_on_audit}
        context = context | {"is_federal_user": is_federal_user}
        context = context | {"route": route}

        return render(request, "audit/compare_submissions.html", context)


def _compare_sac(sac):
    """Compare our sac and return context."""
    has_diffs = False
    has_error = False

    report_id_1, report_id_2, compared = compare_with_prev(sac)
    context = {"comparison": compared}

    nice_names = {}
    for k in compared.keys():
        nice_names[k] = k.replace("_", " ").title()

    for val in compared.values():
        if val == "error":
            has_error = True
            break
        if val == "identical":
            break
        if val["status"] == "error":
            break
        if val["status"] != "same":
            has_diffs = True
            break

    context = context | {"has_diffs": has_diffs}
    context = context | {"has_error": has_error}
    context = context | {"nice_names": nice_names}
    context = context | {"r1": report_id_1}
    context = context | {"r2": report_id_2}

    return context
