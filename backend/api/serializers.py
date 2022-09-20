import json

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from audit.models import SingleAuditChecklist, Access
from api.uei import get_uei_info_from_sam_gov

# Eligibility step messages
SPENDING_THRESHOLD = _(
    "The FAC only accepts submissions from non-Federal entities that spend $750,000 or more in federal awards during its audit period (fiscal period begin dates on or after 12/26/2014) in accordance with Uniform Guidance"
)
USA_BASED = _("The FAC only accepts submissions from U.S.-based entities")
USER_PROVIDED_ORG_TYPE = _(
    "The FAC only accepts submissions from States, Local governments, Indian tribes or Tribal organizations, Institutions of higher education (IHEs), and Non-profits"
)

# Auditee info step messages
AUDITEE_FISCAL_PERIOD_START = _("The fiscal period start date is required")
AUDITEE_FISCAL_PERIOD_END = _("The fiscal period end date is required")

# Access and submission step messages
CERTIFYING_AUDITEE_CONTACT_EMAIL = _(
    "Certifying Auditee Contact email is a required field"
)
CERTIFYING_AUDITOR_CONTACT_EMAIL = _(
    "Certifying Auditor Contact email is a required field"
)
AUDITEE_CONTACTS_LIST = _("Auditee Contacts needs to be a list of emails")
AUDITOR_CONTACTS_LIST = _("Auditor Contacts needs to be a list of emails")


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
                "auditee_address_line_1": sam_response.get("response")
                .get("coreData").get("mailingAddress").get("addressLine1"),
                "auditee_city": sam_response.get("response")
                .get("coreData").get("mailingAddress").get("city"),
                "auditee_state": sam_response.get("response")
                .get("coreData").get("mailingAddress").get("stateOrProvinceCode"),
                "auditee_zip": sam_response.get("response")
                .get("coreData").get("mailingAddress").get("zipCode"),

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

    # auditee_name and auditee_uei optional, fiscal start/end required
    def validate_auditee_fiscal_period_start(self, value):
        if not value:
            raise serializers.ValidationError(AUDITEE_FISCAL_PERIOD_START)
        return value

    def validate_auditee_fiscal_period_end(self, value):
        if not value:
            raise serializers.ValidationError(AUDITEE_FISCAL_PERIOD_END)
        return value


class AccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access
        fields = ["role", "email", "user"]


class AccessAndSubmissionSerializer(serializers.Serializer):
    # This serializer isn't tied to a model, so it's just input fields with the below layout
    certifying_auditee_contact = serializers.EmailField()
    certifying_auditor_contact = serializers.EmailField()
    auditor_contacts = serializers.ListField(
        child=serializers.EmailField(), allow_empty=True, min_length=0
    )
    auditee_contacts = serializers.ListField(
        child=serializers.EmailField(), allow_empty=True, min_length=0
    )


class SingleAuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = "__all__"


class AccessListSerializer(serializers.ModelSerializer):
    auditee_uei = serializers.SerializerMethodField()
    auditee_fiscal_period_end = serializers.SerializerMethodField()
    auditee_name = serializers.SerializerMethodField()
    report_id = serializers.SerializerMethodField()
    submission_status = serializers.SerializerMethodField()

    def get_auditee_uei(self, access):
        return access.sac.auditee_uei

    def get_auditee_fiscal_period_end(self, access):
        return access.sac.auditee_fiscal_period_end

    def get_auditee_name(self, access):
        return access.sac.auditee_name

    def get_report_id(self, access):
        return access.sac.report_id

    def get_submission_status(self, access):
        return access.sac.submission_status

    class Meta:
        model = Access
        fields = [
            "auditee_uei",
            "auditee_fiscal_period_end",
            "auditee_name",
            "role",
            "report_id",
            "submission_status",
        ]
