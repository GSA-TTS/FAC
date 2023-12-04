from django import forms
from django.db import transaction
from django.shortcuts import redirect, render, reverse
from django.views import generic

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    Access,
    SingleAuditChecklist,
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


class ChangeAuditorCertifyingOfficialView(
    SingleAuditChecklistAccessRequiredMixin, generic.View
):
    """
    View for changing the auditor certifying official
    """

    role = "certifying_auditor_contact"
    other_role = "certifying_auditee_contact"

    def get(self, request, *args, **kwargs):
        """
        Show the current auditor certifying official and the form.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        access = Access.objects.get(sac=sac, role=self.role)
        context = {
            "role": self.role,
            "friendly_role": access.get_friendly_role(),
            "auditee_uei": sac.general_information["auditee_uei"],
            "auditee_name": sac.general_information.get("auditee_name"),
            "certifier_name": access.fullname,
            "email": access.email,
            "report_id": report_id,
            "errors": [],
        }

        return render(request, "audit/manage-submission-change-access.html", context)

    def post(self, request, *args, **kwargs):
        """
        Change the current auditor certifying official and redirect to submission
        progress.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        form = ChangeAccessForm(request.POST)
        form.full_clean()
        url = reverse("audit:SubmissionProgress", kwargs={"report_id": report_id})

        if not self.other_role:
            Access(
                sac=sac,
                role=self.role,
                fullname=form.cleaned_data["fullname"],
                email=form.cleaned_data["email"],
            ).save()
            return redirect(url)

        access = Access.objects.get(sac=sac, role=self.role)
        other_access = Access.objects.get(sac=sac, role=self.other_role)
        if form.cleaned_data["email"] == other_access.email:
            context = {
                "role": self.role,
                "friendly_role": access.get_friendly_role(),
                "auditee_uei": sac.general_information["auditee_uei"],
                "auditee_name": sac.general_information.get("auditee_name"),
                "certifier_name": access.fullname,
                "email": access.email,
                "report_id": report_id,
                "errors": [
                    "Cannot use the same email address for both certifying officials."
                ],
            }
            return render(
                request,
                "audit/manage-submission-change-access.html",
                context,
                status=400,
            )

        with transaction.atomic():
            access.delete(removing_user=request.user, removal_event="access-change")

            Access(
                sac=sac,
                role=self.role,
                fullname=form.cleaned_data["fullname"],
                email=form.cleaned_data["email"],
            ).save()

        return redirect(url)


class ChangeAuditeeCertifyingOfficialView(ChangeAuditorCertifyingOfficialView):
    """
    View for changing the auditee certifying official
    """

    role = "certifying_auditee_contact"
    other_role = "certifying_auditor_contact"
