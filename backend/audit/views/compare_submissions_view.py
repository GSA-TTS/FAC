from django.shortcuts import render
from django.views import generic
from django.core.exceptions import PermissionDenied

from audit.viewlib.compare_two_submissions import compare_with_prev, report_id_to_sac
from audit.models import (
    SingleAuditChecklist,
    Access,
)

from audit.models.constants import STATUS
from users.models import UserPermission

import logging

logger = logging.getLogger(__name__)

COMPARE_TEMPLATE = "audit/compare_submissions.html"

PUBLIC_SEARCH_STATUSES = {STATUS.DISSEMINATED, STATUS.RESUBMITTED}

SUBMISSION_DENIED_MESSAGE = "You do not have access to this submission comparison page."

SEARCH_DENIED_MESSAGE = "You do not have access to this search comparison page."


class CompareSubmissionsView(generic.View):

    def get(self, request, report_id, route):
        current_user = request.user

        sac_1 = _get_sac(report_id)
        sac_2 = _get_related_sac(sac_1)

        # Get the accesses for this SAC
        permissions = _get_comparison_permissions(current_user, sac_1, sac_2)

        show_all_data = _get_show_all_data(
            route=route,
            sac_1=sac_1,
            permissions=permissions,
        )

        context = _compare_sac(sac_1, show_all_data)
        context = context | {"is_authenticated": permissions["is_auth_user"]}
        context = context | {"is_on_audit": permissions["is_on_audit"]}
        context = context | {"is_federal_user": permissions["is_federal_user"]}
        context = context | {"route": route}

        return render(request, COMPARE_TEMPLATE, context)


def _get_sac(report_id):
    try:
        return SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist as err:
        raise PermissionDenied(f"Cannot find report id {report_id}") from err


def _get_related_sac(sac):
    related_report_id = _get_related_report_id(sac)

    related_sac = report_id_to_sac(related_report_id)

    if related_sac is None:
        raise PermissionDenied("The associated audit does not exist.")

    return related_sac


def _get_related_report_id(sac):
    resubmission_meta = sac.resubmission_meta or {}

    if "previous_report_id" in resubmission_meta:
        return resubmission_meta["previous_report_id"]

    if "next_report_id" in resubmission_meta:
        return resubmission_meta["next_report_id"]

    raise PermissionDenied(
        "The audit provided does not have any associated audits to compare with."
    )


def _get_show_all_data(*, route, sac_1, permissions):
    if route == "submission":
        return _get_submission_show_all_data(permissions)

    if route == "search":
        return _get_search_show_all_data(sac_1, permissions)

    raise PermissionDenied("Invalid comparison route.")


def _get_submission_show_all_data(permissions):
    if not permissions["is_on_sac1"]:
        raise PermissionDenied(SUBMISSION_DENIED_MESSAGE)

    if permissions["has_tribal"] and not permissions["has_access"]:
        return False
    else:
        return True


def _get_search_show_all_data(sac_1, permissions):
    has_tribal = permissions["has_tribal"]
    has_access = permissions["has_access"]

    is_public_status = sac_1.submission_status in PUBLIC_SEARCH_STATUSES

    if not has_tribal:
        if not is_public_status and not has_access:
            raise PermissionDenied(SEARCH_DENIED_MESSAGE)
        return True

    if has_access:
        return True

    if is_public_status:
        return False

    raise PermissionDenied(SEARCH_DENIED_MESSAGE)


def _get_comparison_permissions(user, sac_1, sac_2):
    is_auth_user = user.is_authenticated

    is_federal_user = _is_federal_user(user)

    is_on_sac1 = _user_has_access_to_sac(user, sac_1)
    is_on_sac2 = _user_has_access_to_sac(user, sac_2)

    has_tribal = _has_sensitive_data(sac_1) or _has_sensitive_data(sac_2)

    is_on_audit = is_on_sac1 and is_on_sac2

    has_access = is_auth_user and (is_on_audit or is_federal_user)

    return {
        "is_auth_user": is_auth_user,
        "is_federal_user": is_federal_user,
        "is_on_sac1": is_on_sac1,
        "is_on_sac2": is_on_sac2,
        "has_tribal": has_tribal,
        "is_on_audit": is_on_audit,
        "has_access": has_access,
    }


def _user_has_access_to_sac(user, sac):
    if not user.is_authenticated:
        return False

    accesses = Access.objects.filter(sac=sac)
    user_ids_on_audit = list(map(lambda acc: acc.user_id, accesses))
    return user.id in user_ids_on_audit


def _is_federal_user(user):
    if not user.is_authenticated:
        return False

    return UserPermission.objects.filter(user_id=user.id).exists()


def _compare_sac(sac, show_all_data):
    """Compare our sac and return context."""
    has_diffs = False
    has_error = False

    report_id_1, report_id_2, compared = compare_with_prev(sac, show_all_data)
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


def _has_sensitive_data(sac):
    has_tribal = False
    data_consent = sac.tribal_data_consent

    if data_consent is not None:
        if data_consent.get("is_tribal_information_authorized_to_be_public") is False:
            has_tribal = True

    return has_tribal
