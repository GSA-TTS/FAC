import logging
from types import SimpleNamespace
from django import forms
from django.db import transaction
from django.shortcuts import redirect, render, reverse
from django.views import generic
from django.http import Http404
from django.core.exceptions import PermissionDenied

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    ACCESS_ROLES,
    Access,
    SingleAuditChecklist,
    Audit,
)

logger = logging.getLogger(__name__)


def _get_friendly_role(role):
    return dict(ACCESS_ROLES)[role]


def _create_and_save_access(sac, audit, role, fullname, email):
    Access.objects.create(
        sac=sac, audit=audit, role=role, fullname=fullname, email=email
    )


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
        # TODO: Update Post SOC Launch
        # We will want to replace "sac" with "audit" once we are ready to deprecate SAC.
        context = self._get_user_role_management_context(sac)

        return render(request, self.template, context)

    # TODO: Update Post SOC Launch
    # We will want to replace "sac" with "audit" under this endpoint when we are ready to deprecate SAC.
    def post(self, request, *args, **kwargs):
        """
        Change the current auditor certifying official and redirect to submission
        progress.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        audit = Audit.objects.find_audit_or_none(report_id=report_id)
        form = ChangeAccessForm(request.POST)
        context = self._get_user_role_management_context(sac)

        form.full_clean()
        if not form.is_valid():
            context = (
                context
                | form.cleaned_data
                | {
                    "errors": form.errors,
                }
            )

            for field, errors in form.errors.items():
                logger.warning(f"Error {field}: {errors}")

            return render(request, self.template, context, status=400)

        url = reverse("audit:ManageSubmission", kwargs={"report_id": report_id})
        fullname = form.cleaned_data["fullname"]
        email = form.cleaned_data["email"]

        # If self.other_role is not set then we're adding an editor:
        if not self.other_role:
            return self._handle_add_editor(
                request, url, sac, audit, report_id, email, fullname
            )

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
                "auditee_uei": (
                    audit.audit.get("general_information", {}).get("auditee_uei", None)
                    if audit
                    else sac.general_information["auditee_uei"]
                ),
                "auditee_name": (
                    audit.audit.get("general_information", {}).get("auditee_name", None)
                    if audit
                    else sac.general_information.get("auditee_name")
                ),
                "certifier_name": access.fullname,
                "email": access.email,
                "report_id": report_id,
                "errors": {
                    "email": "Cannot use the same email address for both certifying officials."
                },
            }
            return render(request, self.template, context, status=400)

        # Only Access, and not SimpleNamespace, has .delete:
        if hasattr(access, "delete"):
            with transaction.atomic():
                access.delete(removing_user=request.user, removal_event="access-change")
                _create_and_save_access(sac, audit, self.role, fullname, email)
        # We know that submissions can get into a bad state where no
        # certifying role(s) exist, so we should support cases where this
        # happens:
        else:
            _create_and_save_access(sac, audit, self.role, fullname, email)

        return redirect(url)

    # TODO: Update Post SOC Launch
    # We will want to replace "sac" with "audit" under this endpoint when we are ready to deprecate SAC.
    def _get_user_role_management_context(self, sac):
        context = {
            "role": self.role,
            "friendly_role": None,
            "auditee_uei": sac.general_information["auditee_uei"],
            "auditee_name": sac.general_information.get("auditee_name"),
            "certifier_name": "",
            "email": "",
            "report_id": sac.report_id,
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

        return context

    # TODO: Update Post SOC Launch
    # We will want to replace "sac" with "audit".
    def _handle_add_editor(self, request, url, sac, audit, report_id, email, fullname):
        # Avoid editors with duplicate emails
        if Access.objects.filter(sac=sac, role=self.role, email=email).exists():
            context = {
                "role": self.role,
                "friendly_role": _get_friendly_role(self.role),
                "auditee_uei": sac.general_information["auditee_uei"],
                "auditee_name": sac.general_information.get("auditee_name"),
                "certifier_name": fullname,
                "email": email,
                "report_id": report_id,
                "errors": {
                    "email": f"{email} is already in use by another editor for this audit."
                },
            }

            return render(request, self.template, context, status=400)
        else:
            _create_and_save_access(sac, audit, self.role, fullname, email)
            return redirect(url)


class RemoveEditorView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    """
    View for removing the audit access of an editor.
    """

    template = "audit/remove-editor-access.html"
    role = "editor"

    # TODO: Update Post SOC Launch
    # We will want to replace "sac" with "audit".
    def get(self, request, *args, **kwargs):
        """
        Show the current editor and the form.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)

        if not Access.objects.filter(
            email=request.user.email, sac=sac, role=self.role
        ).exists():
            raise PermissionDenied(
                "Only Audit Editors may remove audit access for other Audit Editors."
            )

        editor_id = request.GET.get("id", None)

        try:
            access_to_remove = Access.objects.get(id=editor_id, sac=sac, role=self.role)
        except Access.DoesNotExist as e:
            raise Http404() from e

        context = {
            "auditee_uei": sac.general_information["auditee_uei"],
            "auditee_name": sac.general_information.get("auditee_name"),
            "editor_id": access_to_remove.id,
            "name": access_to_remove.fullname,
            "email": access_to_remove.email,
            "report_id": sac.report_id,
            "is_editor_removing_self": request.user.email == access_to_remove.email,
            "errors": [],
        }

        return render(request, "audit/remove-editor-access.html", context)

    # TODO: Update Post SOC Launch
    # We will want to replace "sac" with "audit".
    def post(self, request, *args, **kwargs):
        """
        Remove the editor and redirect to manage submission.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)

        if not Access.objects.filter(
            email=request.user.email, sac=sac, role=self.role
        ).exists():
            raise PermissionDenied(
                "Only Audit Editors may remove audit access for other Audit Editors."
            )

        editor_id = request.POST.get("editor_id")

        try:
            access_to_remove = Access.objects.get(id=editor_id, sac=sac, role=self.role)
        except Access.DoesNotExist as e:
            raise Http404() from e

        if request.user.email != access_to_remove.email:
            access_to_remove.delete()
        else:
            context = {
                "auditee_uei": sac.general_information["auditee_uei"],
                "auditee_name": sac.general_information.get("auditee_name"),
                "editor_id": access_to_remove.id,
                "name": access_to_remove.fullname,
                "email": access_to_remove.email,
                "report_id": sac.report_id,
                "is_editor_removing_self": True,
                "errors": {"email": "You cannot remove your own audit access"},
            }

            return render(request, "audit/remove-editor-access.html", context)

        url = reverse("audit:ManageSubmission", kwargs={"report_id": report_id})
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
