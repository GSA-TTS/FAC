from types import SimpleNamespace
from django import forms
from django.db import transaction
from django.shortcuts import redirect, render, reverse
from django.views import generic

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    ACCESS_ROLES,
    Access,
    SingleAuditChecklist,
)


def _get_friendly_role(role):
    return dict(ACCESS_ROLES)[role]


def _create_and_save_access(sac, role, fullname, email):
    Access.objects.create(sac=sac, role=role, fullname=fullname, email=email)


class ChangeAccessForm(forms.Form):
    """
    Form for changing access. The view class, not this class, has the responsibility for handling whether we’re deleting access (in the cases where only one user can have the role) or adding access (in the cases where multiple users can have the role).
    """

    fullname = forms.CharField()
    email = forms.EmailField()
    # email_confirm = forms.EmailField()

    # def clean(self):
    #     cleaned = super().clean()
    #     if cleaned.get("email") != cleaned.get("email_confirm"):
    #         raise ValidationError(
    #             "Email address and confirmed email address must match"
    #         )


class ChangeOrAddRoleView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    """
    View for adding a new editor; also has logic for changing certifying roles.
    """

    role = "editor"
    other_role = ""
    template = "audit/manage-submission-change-access.html"

    def get(self, request, *args, **kwargs):
        """
        Show the current auditor certifying official and the form.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        context = {
            "role": self.role,
            "friendly_role": None,
            "auditee_uei": sac.general_information["auditee_uei"],
            "auditee_name": sac.general_information.get("auditee_name"),
            "certifier_name": None,
            "email": None,
            "report_id": report_id,
            "errors": [],
        }
        if self.role != "editor":
            try:
                access = Access.objects.get(sac=sac, role=self.role)
            except Access.DoesNotExist:
                access = SimpleNamespace(
                    fullname="UNASSIGNED ROLE", email="UNASSIGNED ROLE", role=self.role
                )

            context = context | {
                "friendly_role": _get_friendly_role(access.role),
                "certifier_name": access.fullname,
                "email": access.email,
            }

        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        """
        Change the current auditor certifying official and redirect to submission
        progress.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        form = ChangeAccessForm(request.POST)
        form.full_clean()
        url = reverse("audit:ManageSubmission", kwargs={"report_id": report_id})
        fullname = form.cleaned_data["fullname"]
        email = form.cleaned_data["email"]

        # Only if we have self.other_role do we need further checks:
        if not self.other_role:
            _create_and_save_access(sac, self.role, fullname, email)
            return redirect(url)

        # We need the existing role assignment, if any, to delete it:
        try:
            access = Access.objects.get(sac=sac, role=self.role)
        except Access.DoesNotExist:
            access = SimpleNamespace(
                fullname="UNASSIGNED ROLE", email="UNASSIGNED ROLE", role=self.role
            )

        # We need the other role assignment, if any, to compare email addresses:
        try:
            other_access = Access.objects.get(sac=sac, role=self.other_role)
            other_access_email = other_access.email
        except Access.DoesNotExist:
            other_access_email = None

        if email == other_access_email:
            context = {
                "role": self.role,
                "friendly_role": _get_friendly_role(self.role),
                "auditee_uei": sac.general_information["auditee_uei"],
                "auditee_name": sac.general_information.get("auditee_name"),
                "certifier_name": access.fullname,
                "email": access.email,
                "report_id": report_id,
                "errors": [
                    "Cannot use the same email address for both certifying officials."
                ],
            }
            return render(request, self.template, context, status=400)

        # Only Access, and not SimpleNamespace, has .delete:
        if hasattr(access, "delete"):
            with transaction.atomic():
                access.delete(removing_user=request.user, removal_event="access-change")
                _create_and_save_access(sac, self.role, fullname, email)
        # We know that submissions can get into a bad state where no
        # certifying role(s) exist, so we should support cases where this
        # happens:
        else:
            _create_and_save_access(sac, self.role, fullname, email)

        return redirect(url)


class ChangeAuditorCertifyingOfficialView(ChangeOrAddRoleView):
    """
    View for changing the auditor certifying official
    """

    role = "certifying_auditor_contact"
    other_role = "certifying_auditee_contact"


class ChangeAuditeeCertifyingOfficialView(ChangeOrAddRoleView):
    """
    View for changing the auditee certifying official
    """

    role = "certifying_auditee_contact"
    other_role = "certifying_auditor_contact"
