from functools import partial
from django.shortcuts import render, reverse
from django.views import generic

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    ACCESS_ROLES,
    Access,
    Audit,
)
from audit.models.utils import get_friendly_submission_status


def _get_friendly_role(role):
    return dict(ACCESS_ROLES)[role]


class ManageSubmissionView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    """
    View for managing a submission.
    """

    def get(self, request, *args, **kwargs):
        """
        Show:

        +   report_id
        +   Entity name
        +   UEI
        +   Audit fiscal period
        +   Submission status
        +   Table with:

            +   user names
            +   user roles
            +   user email addresses
            +   user account existence?
        +   Links to:

            +   submission progress page
            +   change auditee certifying official
            +   change auditor certifying official
        """

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

        def _get_url_from_viewname(viewname: str, report_id: str | None = None) -> str:
            kwargs = {"kwargs": {"report_id": report_id}} if report_id else {}
            return reverse(f"audit:{viewname}", **kwargs)

        report_id = kwargs["report_id"]
        audit = Audit.objects.get(report_id=report_id)
        general_information = audit.audit.get("general_information", {})

        accesses = Access.objects.filter(audit=audit).order_by("role")
        base_entries = list(map(_user_entry, accesses))
        period_start = general_information.get("auditee_fiscal_period_start")
        period_end = general_information.get("auditee_fiscal_period_end")
        _url = partial(_get_url_from_viewname, report_id=report_id)

        # Handle missing certifier roles:
        entries_to_add = []
        for role in ("certifying_auditee_contact", "certifying_auditor_contact"):
            frole = _get_friendly_role(role)
            if not [row for row in base_entries if row["role"] == frole]:
                entry = {
                    "name": "UNASSIGNED ROLE",
                    "email": "UNASSIGNED ROLE",
                    "role": frole,
                    "user_exists": False,
                    "never_logged_in_flag": "*",
                }
                entries_to_add.append(entry)
        entries = base_entries + entries_to_add

        context = {
            "auditee_uei": audit.auditee_uei,
            "auditee_name": audit.auditee_name,
            "report_id": report_id,
            "entries": entries,
            "status": get_friendly_submission_status(audit.submission_status),
            "period": f"{period_start} to {period_end}",
            "progress_url": _url("SubmissionProgress"),
            "change_cert_auditee_url": _url("ChangeAuditeeCertifyingOfficial"),
            "change_cert_auditor_url": _url("ChangeAuditorCertifyingOfficial"),
            "add_editor_url": _url("ChangeOrAddRoleView"),
            "remove_editor_url": _url("RemoveEditorView"),
            "user_is_editor": Access.objects.filter(
                audit=audit, email=request.user.email, role="editor"
            ),
        }

        return render(request, "audit/manage-submission.html", context)
