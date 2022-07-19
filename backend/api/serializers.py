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
CERTIFYING_CONTACT_EMAIL = _(
    "Certifying Auditee and Certifying Auditor Contact emails are required fields"
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


class AccessAndSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access
        fields = ["role", "email", "user"]

    def validate(self, data):
        """
        The data here should be a series of role/email pairs.
        We want to verify that there is one and only one certifying_auditee_contact
        and one and only one certifying_auditor_contact listed.

        We think the data will look like this:

        {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com",  "d@d.com"],
            "auditee_contacts": ["e@e.com",  "f@f.com"],
        }

        """

        # Are both required certifying email fields there?
        if not data.get("certifying_auditee_contact") or not data.get("certifying_auditor_contact"):
            raise serializers.ValidationError(CERTIFYING_CONTACT_EMAIL)

        # (This may change pending advice from design)
        # Are both required lists of contacts there?
        if not data.get("auditor_contacts") or not isinstance(data.get("auditor_contacts"), list):
            raise serializers.ValidationError(AUDITOR_CONTACTS_LIST)
        if not data.get("auditee_contacts") or not isinstance(data.get("auditee_contacts"), list):
            raise serializers.ValidationError(AUDITEE_CONTACTS_LIST)

        # Passes
        return data

class SingleAuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleAuditChecklist
        fields = "__all__"
