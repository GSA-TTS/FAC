from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import generic

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    ACCESS_ROLES,
    Access,
    SingleAuditChecklist,
)


class ChangeAccessForm(forms.Form):
    """
    For for changing access. The view class, not this class, has the responsibility for handling whether we’re deleting access (in the cases where only one user can have the role) or adding access (in the cases where multiple users can have the role).
    """

    name = forms.CharField()
    email = forms.EmailField()
    email_confirm = forms.EmailField()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("email") != cleaned.get("email_confirm"):
            raise ValidationError(
                "Email address and confirmed email address must match"
            )


class ChangeAuditorCertifyingOfficialView(
    SingleAuditChecklistAccessRequiredMixin, generic.View
):
    """
    View for changing the auditor certifying official
    """

    def get(self, request, *args, **kwargs):
        """
        Show the current auditor certifying official and the form.
        """
        role = "certifying_auditor_contact"
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        # TODO: should we account for the possibility of this role being absent?
        access = Access.objects.get(sac=sac, role=role)
        friendly_role = [r for r in ACCESS_ROLES if r[0] == role][0][1]
        context = {
            "role": role,
            "friendly_role": friendly_role,
            "auditee_uei": sac.general_information["auditee_uei"],
            "auditee_name": sac.general_information.get("auditee_name"),
            "certifier_name": access.fullname,
            "email": access.email,
            "report_id": report_id,
        }

        return render(request, "audit/manage-submission-change-access.html", context)
