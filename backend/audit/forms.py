from django.forms import ModelForm
from .models import SingleAuditChecklist


class SubmissionForm(ModelForm):
    class Meta:
        model = SingleAuditChecklist
        fields = "__all__"
