import json

from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from audit.models import SingleAuditChecklist, Access
from api.uei import get_uei_info_from_sam_gov
from audit.validators import (
    validate_general_information_json,
)
from config.settings import CHARACTER_LIMITS_GENERAL


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
AUDITEE_CONTACTS_LIST = _(
    "Auditee Contacts needs to be a list of full names and emails"
)
AUDITOR_CONTACTS_LIST = _(
    "Auditor Contacts needs to be a list of full names and emails"
)

CERTIFIERS_HAVE_DIFFERENT_EMAILS = _(
    "The certifying auditee and certifying auditor must have different email addresses."
)


class EligibilitySerializer(serializers.Serializer):
    user_provided_organization_type = serializers.CharField()
    met_spending_threshold = serializers.BooleanField()
    is_usa_based = serializers.BooleanField()

    def validate(self, data):
        try:
            validate_general_information_json(data, False)
            return data
        except ValidationError as err:
            raise serializers.ValidationError(_(err.message)) from err

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


class UEISerializer(serializers.Serializer):
    """
    Does a UEI request against the SAM.gov API and returns a flattened shape
    containing only the fields we're interested in.

    The below operations are nested and mixed among functions, rather than done
    serially, but the approximate order of operations is:

        +   Assemble the parameters to pass to the API.
            Mostly in api.uei.get_uei_info_from_sam_gov.
        +   Make the API request.
            api.uei.call_sam_api
        +   Check for high-level errors.
            api.uei.get_uei_info_from_sam_gov
        +   Extract the JSON for the individual record out of the response and check
        for some other errors.
            api.uei.parse_sam_uei_json
        +   For a specific class of error, retry the API call with different
        parameters.
            api.uei.get_uei_info_from_sam_gov
            api.uei.call_sam_api
            api.uei.parse_sam_uei_json
        +   If we don't have errors by that point, flatten the data.
            api.serializsers.UEISerializer.validate_auditee_uei
        +   If we don't encounter errors at that point, return the flattened data.
            api.serializsers.UEISerializer.validate_auditee_uei

    """

    auditee_uei = serializers.CharField()

    def validate_auditee_uei(self, value):
        """
        Flattens the UEI response info and returns this shape:

            {
                "auditee_uei": …,
                "auditee_name": …,
                "auditee_fiscal_year_end_date": …,
                "auditee_address_line_1": …,
                "auditee_city": …,
                "auditee_state": …,
                "auditee_zip": …,
            }

        Will provide default error-message-like values (such as “No address in SAM.gov)
        if the keys are missing, but if the SAM.gov fields are present but empty, we
        return the empty strings.

        """
        sam_response = get_uei_info_from_sam_gov(value)
        if sam_response.get("errors"):
            raise serializers.ValidationError(sam_response.get("errors"))

        entity_registration = sam_response.get("response")["entityRegistration"]
        core = sam_response.get("response")["coreData"]

        basic_data = {
            "auditee_uei": value,
            "auditee_name": entity_registration.get("legalBusinessName"),
        }
        addr_key = "mailingAddress" if "mailingAddress" in core else "physicalAddress"

        mailing_data = {
            "auditee_address_line_1": "No address in SAM.gov.",
            "auditee_city": "No address in SAM.gov.",
            "auditee_state": "No address in SAM.gov.",
            "auditee_zip": "No address in SAM.gov.",
        }

        if addr_key in core:
            mailing_data = {
                "auditee_address_line_1": core.get(addr_key).get("addressLine1"),
                "auditee_city": core.get(addr_key).get("city"),
                "auditee_state": core.get(addr_key).get("stateOrProvinceCode"),
                "auditee_zip": core.get(addr_key).get("zipCode"),
            }

        # 2023-10-10: Entities with a samRegistered value of No may be missing
        # some fields from coreData entirely.
        entity_information = core.get("entityInformation", {})
        extra_data = {
            "auditee_fiscal_year_end_date": entity_information.get(
                "fiscalYearEndCloseDate", "No fiscal year end date in SAM.gov."
            ),
        }
        return json.dumps(basic_data | mailing_data | extra_data)


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


class AccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access
        fields = ["role", "email", "user"]


class AccessAndSubmissionSerializer(serializers.Serializer):
    # This serializer isn't tied to a model, so it's just input fields with the below layout
    certifying_auditee_contact_fullname = serializers.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_contact_name"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_contact_name"]["max"],
    )
    certifying_auditee_contact_email = serializers.EmailField(
        min_length=CHARACTER_LIMITS_GENERAL["auditee_email"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditee_email"]["max"],
    )
    certifying_auditor_contact_fullname = serializers.CharField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_contact_name"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_contact_name"]["max"],
    )
    certifying_auditor_contact_email = serializers.EmailField(
        min_length=CHARACTER_LIMITS_GENERAL["auditor_email"]["min"],
        max_length=CHARACTER_LIMITS_GENERAL["auditor_email"]["max"],
    )
    auditor_contacts_email = serializers.ListField(
        child=serializers.EmailField(
            required=False,
            allow_null=True,
            allow_blank=True,
            min_length=CHARACTER_LIMITS_GENERAL["auditor_email"]["min"],
            max_length=CHARACTER_LIMITS_GENERAL["auditor_email"]["max"],
        ),
        allow_empty=True,
    )
    auditee_contacts_email = serializers.ListField(
        child=serializers.EmailField(
            required=False,
            allow_null=True,
            allow_blank=True,
            min_length=CHARACTER_LIMITS_GENERAL["auditee_email"]["min"],
            max_length=CHARACTER_LIMITS_GENERAL["auditee_email"]["max"],
        ),
        allow_empty=True,
    )
    auditor_contacts_fullname = serializers.ListField(
        child=serializers.CharField(
            required=False,
            allow_null=True,
            allow_blank=True,
            min_length=CHARACTER_LIMITS_GENERAL["auditor_contact_name"]["min"],
            max_length=CHARACTER_LIMITS_GENERAL["auditor_contact_name"]["max"],
        ),
        allow_empty=True,
    )
    auditee_contacts_fullname = serializers.ListField(
        child=serializers.CharField(
            required=False,
            allow_null=True,
            allow_blank=True,
            min_length=CHARACTER_LIMITS_GENERAL["auditee_contact_name"]["min"],
            max_length=CHARACTER_LIMITS_GENERAL["auditee_contact_name"]["max"],
        ),
        allow_empty=True,
    )

    def validate(self, data):
        certifying_auditee_contact_email = data["certifying_auditee_contact_email"]
        certifying_auditor_contact_email = data["certifying_auditor_contact_email"]

        if (
            certifying_auditee_contact_email.lower()
            == certifying_auditor_contact_email.lower()
        ):
            raise ValidationError(CERTIFIERS_HAVE_DIFFERENT_EMAILS)

        return data


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
