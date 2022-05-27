import json

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from audit.models import SingleAuditChecklist, Access
from api.uei import get_uei_info_from_sam_gov


SPENDING_THRESHOLD = _(
    "The FAC only accepts submissions from non-Federal entities that spend $750,000 or more in federal awards during its audit period (fiscal period begin dates on or after 12/26/2014) in accordance with Uniform Guidance"
)
USA_BASED = _("The FAC only accepts submissions from U.S.-based entities")
USER_PROVIDED_ORG_TYPE = _(
    "The FAC only accepts submissions from States, Local governments, Indian tribes or Tribal organizations, Institutions of higher education (IHEs), and Non-profits"
)


class EligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = [
            "user_provided_organization_type",
            "met_spending_threshold",
            "is_usa_based",
        ]

    def validate_is_usa_based(self, value):
        if not value:
            raise serializers.ValidationError(USA_BASED)
        return value

    def validate_met_spending_threshold(self, value):
        if not value:
            raise serializers.ValidationError(SPENDING_THRESHOLD)
        return value

    def validate_user_provided_organization_type(self, value):
        if value == "none":
            raise serializers.ValidationError(USER_PROVIDED_ORG_TYPE)
        return value


class UEISerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = ["auditee_uei"]

    def validate_auditee_uei(self, value):
        sam_response = get_uei_info_from_sam_gov(value)
        if sam_response.get("errors"):
            raise serializers.ValidationError(sam_response.get("errors"))
        return json.dumps(
            {
                "auditee_uei": value,
                "auditee_name": sam_response.get("response")
                .get("entityRegistration")
                .get("legalBusinessName"),
                "auditee_fiscal_year_end_date": sam_response.get("response")
                .get("coreData")
                .get("entityInformation")
                .get("fiscalYearEndCloseDate"),
            }
        )


class AuditeeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = [
            "auditee_name",
            "auditee_uei",
            "auditee_fiscal_period_start",
            "auditee_fiscal_period_end",
        ]


class AccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access
        fields = ["role", "email", "user_id"]


class SingleAuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = "__all__"
