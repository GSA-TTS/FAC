from django.shortcuts import render
from django.views import generic
from django.core.exceptions import PermissionDenied

from audit.viewlib.compare_two_submissions import compare_with_prev, report_id_to_sac
from audit.models import (
    SingleAuditChecklist,
    Access,
)

from audit.models.constants import STATUS

import logging

logger = logging.getLogger(__name__)

COMPARE_TEMPLATE = "audit/compare_submissions.html"

PUBLIC_SEARCH_STATUSES = {STATUS.DISSEMINATED, STATUS.RESUBMITTED}

SUBMISSION_DENIED_MESSAGE = "You do not have access to this submission comparison page."

SEARCH_DENIED_MESSAGE = "You do not have access to this search comparison page."


def _get_sac(report_id):
    """Get a SAC using a report ID."""
    try:
        return SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist as err:
        raise PermissionDenied(f"Cannot find report id {report_id}") from err


def _get_previous_sac(sac):
    """Use a resubmission SAC, get its previous SAC."""
    previous_report_id = _get_previous_report_id(sac)

    previous_sac = report_id_to_sac(previous_report_id)

    if previous_sac is None:
        raise PermissionDenied("The associated audit does not exist.")

    return previous_sac


def _get_previous_report_id(sac):
    """Search SAC resubmission_meta for 'previous_report_id'."""
    resubmission_meta = sac.resubmission_meta or {}

    if "previous_report_id" in resubmission_meta:
        return resubmission_meta["previous_report_id"]

    raise PermissionDenied(
        "The audit provided does not have any associated audits to compare with."
    )


def _get_show_all_data(*, route, sac, permissions):
    """
    Assemble decision to 'show all data' for a comparison.

    Returns:
        bool: True to 'show all data';  False to 'show partial data'
    """
    if route == "submission":
        return _get_submissions_show_all_data(permissions)

    if route == "search":
        return _get_search_show_all_data(sac, permissions)

    raise PermissionDenied("Invalid comparison route.")


def _get_submissions_show_all_data(permissions):
    """Determine what user can view during Submission.

    Args:
        sac: The single audit checklist
        permissions: The user's permissions.

    Returns:
        bool: True to 'show all data';  False to 'show partial data'
    """
    if not permissions["is_on_audit"]:
        raise PermissionDenied(SUBMISSION_DENIED_MESSAGE)

    has_private_tribal = permissions["has_private_tribal"]
    is_on_both_audits = permissions["is_on_both_audits"]

    if has_private_tribal:
        if is_on_both_audits:
            return True
        else:
            return False
    else:
        return True


def _get_search_show_all_data(sac, permissions):
    """Determine what user can view during Search.

    Args:
        sac: The single audit checklist
        permissions: The user's permissions.

    Returns:
        bool: True to 'show all data';  False to 'show partial data'
    """
    has_private_tribal = permissions["has_private_tribal"]
    is_on_both_audits = permissions["is_on_both_audits"]
    is_on_audit = permissions["is_on_audit"]
    is_public_status = sac.submission_status in PUBLIC_SEARCH_STATUSES

    if not is_public_status and not is_on_audit:
        raise PermissionDenied(SEARCH_DENIED_MESSAGE)

    if has_private_tribal:
        if is_on_both_audits:
            return True
        else:
            return False
    else:
        return True


def _get_comparison_permissions(user, current_sac, previous_sac):
    """Collect permissions to determine what this user is allowed to see when comparing SACs."""
    is_auth_user = user.is_authenticated

    is_on_current_sac = _user_has_access_to_sac(user, current_sac)
    is_on_previous_sac = _user_has_access_to_sac(user, previous_sac)

    has_private_tribal = _has_sensitive_data(current_sac) or _has_sensitive_data(
        previous_sac
    )

    is_on_both_audits = is_on_current_sac and is_on_previous_sac

    return {
        "is_auth_user": is_auth_user,
        "has_private_tribal": has_private_tribal,
        "is_on_audit": is_on_current_sac,
        "is_on_both_audits": is_on_both_audits,
    }


def _user_has_access_to_sac(user, sac):
    """Determine if 'user' has access to this 'sac'."""
    if not user.is_authenticated:
        return False

    accesses = Access.objects.filter(sac=sac)
    user_ids_on_audit = list(map(lambda acc: acc.user_id, accesses))
    return user.id in user_ids_on_audit


def _compare_sac(sac, show_all_data):
    """Compare our sac and return context."""
    has_diffs = False
    has_error = False

    report_id_1, report_id_2, compared = compare_with_prev(sac, show_all_data)

    nice_names = {key: key.replace("_", " ").title() for key in compared.keys()}

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

    return {
        "comparison": compared,
        "has_diffs": has_diffs,
        "has_error": has_error,
        "nice_names": nice_names,
        "r1": report_id_1,
        "r2": report_id_2,
    }


def _has_sensitive_data(sac):
    """Determine if this SAC uses private tribal data."""
    has_private_tribal = False
    data_consent = sac.tribal_data_consent

    if data_consent is not None:
        if data_consent.get("is_tribal_information_authorized_to_be_public") is False:
            has_private_tribal = True

    return has_private_tribal


class CompareSubmissionsView(generic.View):
    """Compare Submission view used in 'submission' and 'search' flows."""

    def get(self, request, report_id, route):
        """
        With a resubmission report_id and route this directs the user to view comparisons between SACs.

        Special care is taken to view 'private' tribal data
        """
        current_user = request.user
        current_sac = _get_sac(report_id)
        previous_sac = _get_previous_sac(current_sac)

        # Get the accesses for this SAC
        permissions = _get_comparison_permissions(
            current_user, current_sac, previous_sac
        )

        show_all_data = _get_show_all_data(
            route=route,
            sac=current_sac,
            permissions=permissions,
        )

        context = _compare_sac(current_sac, show_all_data)
        context.update(
            {
                "is_authenticated": permissions["is_auth_user"],
                "is_on_audit": permissions["is_on_audit"],
                "route": route,
            }
        )

        return render(request, COMPARE_TEMPLATE, context)
