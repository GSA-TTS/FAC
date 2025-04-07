from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from audit.models import Access
from config.settings import CHARACTER_LIMITS_GENERAL

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


class AccessListSerializer(serializers.ModelSerializer):
    auditee_uei = serializers.SerializerMethodField()
    auditee_fiscal_period_end = serializers.SerializerMethodField()
    auditee_name = serializers.SerializerMethodField()
    report_id = serializers.SerializerMethodField()
    submission_status = serializers.SerializerMethodField()

    @staticmethod
    def get_auditee_uei(access):
        return access.audit.auditee_uei

    @staticmethod
    def get_auditee_fiscal_period_end(access):
        return access.audit.auditee_fiscal_period_end

    @staticmethod
    def get_auditee_name(access):
        return access.audit.audit.auditee_name

    @staticmethod
    def get_report_id(access):
        return access.audit.report_id

    @staticmethod
    def get_submission_status(access):
        return access.audit.submission_status

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
