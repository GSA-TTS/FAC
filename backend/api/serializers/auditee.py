from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from audit.validators import (
    validate_general_information_json,
)

# Auditee info step messages
AUDITEE_FISCAL_PERIOD_START = _("The fiscal period start date is required")
AUDITEE_FISCAL_PERIOD_END = _("The fiscal period end date is required")


class AuditeeInfoSerializer(serializers.Serializer):
    auditee_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    auditee_uei = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    auditee_fiscal_period_start = serializers.CharField()
    auditee_fiscal_period_end = serializers.CharField()

    def validate(self, data):
        try:
            validate_general_information_json(data, False)
            return data
        except ValidationError as err:
            raise serializers.ValidationError(_(err.message)) from err

    # auditee_name and auditee_uei optional, fiscal start/end required
    def validate_auditee_fiscal_period_start(self, value):
        if not value:
            raise serializers.ValidationError(AUDITEE_FISCAL_PERIOD_START)
        return value

    def validate_auditee_fiscal_period_end(self, value):
        if not value:
            raise serializers.ValidationError(AUDITEE_FISCAL_PERIOD_END)
        return value
