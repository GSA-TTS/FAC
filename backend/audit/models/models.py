from datetime import timedelta
from itertools import chain
import json
import logging

from django.db import models
from django.db.transaction import TransactionManagementError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _
from django.utils import timezone as django_timezone

import audit.cross_validation
from audit.cross_validation.naming import SECTION_NAMES
from audit.intake_to_dissemination import IntakeToDissemination
from audit.validators import (
    validate_additional_ueis_json,
    validate_additional_eins_json,
    validate_corrective_action_plan_json,
    validate_excel_file,
    validate_federal_award_json,
    validate_findings_text_json,
    validate_findings_uniform_guidance_json,
    validate_general_information_json,
    validate_secondary_auditors_json,
    validate_notes_to_sefa_json,
    validate_single_audit_report_file,
    validate_auditor_certification_json,
    validate_auditee_certification_json,
    validate_tribal_data_consent_json,
    validate_audit_information_json,
    validate_component_page_numbers,
)
from audit.utils import FORM_SECTION_HANDLERS
from support.cog_over import compute_cog_over, record_cog_assignment
from .submission_event import SubmissionEvent

User = get_user_model()

logger = logging.getLogger(__name__)


def generate_sac_report_id(end_date=None, source="GSAFAC", count=None):
    """
    Convenience method for generating report_id, a value consisting of:

        -   Four-digit year based on submission fiscal end date.
        -   Two-digit month based on submission fiscal end date.
        -   Audit source: either GSAFAC or CENSUS.
        -   Zero-padded 10-digit numeric monotonically increasing.
        -   Separated by hyphens.

    For example: `2023-09-GSAFAC-0000000001`, `2020-09-CENSUS-0000000001`.
    """
    source = source.upper()
    if source not in ("CENSUS", "GSAFAC"):
        raise Exception("Unknown source for report_id")
    if not end_date:
        raise Exception("generate_sac_report_id requires end_date.")
    if not count:
        count = str(SingleAuditChecklist.objects.count() + 1).zfill(10)
    year, month, _ = end_date.split("-")
    if not (int(year) >= 2000 and int(year) < 2200):
        raise Exception("Unexpected year value for report_id")
    if int(month) not in range(1, 13):
        raise Exception("Unexpected month value for report_id")
    separator = "-"
    report_id = separator.join([year, month, source, count])
    return report_id


def one_month_from_today():
    return django_timezone.now() + timedelta(days=30)


class SingleAuditChecklistManager(models.Manager):
    """Manager for SAC"""

    def create(self, **obj_data):
        """
        Custom create method so that we can add derived fields.

        Currently only used for report_id, a value consisting of:

            -   Four-digit year based on submission fiscal end date.
            -   Two-digit month based on submission fiscal end date.
            -   Audit source: either GSAFAC or CENSUS.
            -   Zero-padded 10-digit numeric monotonically increasing.
            -   Separated by hyphens.

        For example: `2023-09-GSAFAC-0000000001`, `2020-09-CENSUS-0000000001`.

        """

        # remove event_user & event_type keys so that they're not passed into super().create below
        event_user = obj_data.pop("event_user", None)
        event_type = obj_data.pop("event_type", None)

        end_date = obj_data["general_information"]["auditee_fiscal_period_end"]
        report_id = generate_sac_report_id(end_date=end_date, source="GSAFAC")
        updated = obj_data | {"report_id": report_id}

        result = super().create(**updated)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=result,
                user=event_user,
                event=event_type,
            )

        return result


def camel_to_snake(raw: str) -> str:
    """Convert camel case to snake_case."""
    text = f"{raw[0].lower()}{raw[1:]}"
    return "".join(c if c.islower() else f"_{c.lower()}" for c in text)


def json_property_mixin_generator(name, fname=None, toplevel=None, classname=None):
    """Generates a mixin class named classname, using the top-level fields
    in the properties field in the file named fname, accessing those fields
    in the JSON field named toplevel.
    If the optional arguments aren't provided, generate them from name."""
    filename = fname or f"{name}.schema.json"
    toplevelproperty = toplevel or camel_to_snake(name)
    mixinname = classname or f"{name}Mixin"

    def _wrapper(key):
        def inner(self):
            try:
                return getattr(self, toplevelproperty)[key]
            except KeyError:
                logger.warning("Key %s not found in SAC", key)
            except TypeError:
                logger.warning("Type error trying to get %s from SAC %s", key, self)
            return None

        return inner

    schemadir = settings.SECTION_SCHEMA_DIR
    schemafile = schemadir / filename
    schema = json.loads(schemafile.read_text())
    attrdict = {k: property(_wrapper(k)) for k in schema["properties"]}
    return type(mixinname, (), attrdict)


GeneralInformationMixin = json_property_mixin_generator("GeneralInformation")


class LateChangeError(Exception):
    """
    Exception covering attempts to change submissions that don't have the in_progress
    status.
    """


class STATUS:
    """
    The possible states of a submission.
    """

    IN_PROGRESS = "in_progress"
    READY_FOR_CERTIFICATION = "ready_for_certification"
    AUDITOR_CERTIFIED = "auditor_certified"
    AUDITEE_CERTIFIED = "auditee_certified"
    CERTIFIED = "certified"
    SUBMITTED = "submitted"
    DISSEMINATED = "disseminated"
    FLAGGED_FOR_REMOVAL = "flagged_for_removal"


class SingleAuditChecklist(models.Model, GeneralInformationMixin):  # type: ignore
    """
    Monolithic Single Audit Checklist.
    """

    # Class management machinery:
    class Meta:
        """We need to set the name for the admin view."""

        verbose_name = "SF-SAC"
        verbose_name_plural = "SF-SACs"

    objects = SingleAuditChecklistManager()

    # Method overrides:
    def __str__(self):
        return f"#{self.id}--{self.report_id}--{self.auditee_uei}"

    def save(self, *args, **kwargs):
        """
        Call _reject_late_changes() to verify that a submission that's no longer
        in progress isn't being altered; skip this if we know this submission is
        in progress.
        """
        if self.submission_status != STATUS.IN_PROGRESS:
            try:
                self._reject_late_changes()
            except LateChangeError as err:
                raise LateChangeError from err

        event_user = kwargs.get("event_user")
        event_type = kwargs.get("event_type")
        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=self,
                user=event_user,
                event=event_type,
            )

        return super().save()

    def disseminate(self):
        """
        Cognizant/Oversight agency assignment followed by dissemination
        ETL.
        """
        try:
            if not self.cognizant_agency and not self.oversight_agency:
                self.assign_cog_over()
            intake_to_dissem = IntakeToDissemination(self)
            intake_to_dissem.load_all()
            intake_to_dissem.save_dissemination_objects()
            if intake_to_dissem.errors:
                return {"errors": intake_to_dissem.errors}
        except TransactionManagementError as err:
            # We want to re-raise this to catch at the view level because we
            # think it's due to a race condition where the user's submission
            # has been disseminated successfully; see
            # https://github.com/GSA-TTS/FAC/issues/3347
            raise err
        # TODO: figure out what narrower exceptions to catch here
        except Exception as err:
            return {"errors": [err]}

        return None

    def assign_cog_over(self):
        """
        Function that the FAC app uses when a submission is completed and cog_over needs to be assigned.
        """
        if not self.federal_awards:
            logger.warning(
                "Trying to determine cog_over for a self with zero awards with status = %s",
                self.submission_status,
            )

        audit_date = self.general_information["auditee_fiscal_period_end"]
        audit_year = int(audit_date.split("-")[0])
        cognizant_agency, oversight_agency = compute_cog_over(
            self.federal_awards,
            self.submission_status,
            self.ein,
            self.auditee_uei,
            audit_year,
        )
        if oversight_agency:
            self.oversight_agency = oversight_agency
            self.save()
            return
        if cognizant_agency:
            self.cognizant_agency = cognizant_agency
            self.save()
            record_cog_assignment(self.report_id, self.submitted_by, cognizant_agency)

    def _reject_late_changes(self):
        """
        This should only be called if status isn't STATUS.IN_PROGRESS.
        If there have been relevant changes, raise an AssertionError.
        Here, "relevant" means anything other than fields related to the status
        transition change itself.
        """
        try:
            prior_obj = SingleAuditChecklist.objects.get(pk=self.pk)
        except SingleAuditChecklist.DoesNotExist:
            # No prior instance exists, so it's a new submission.
            return True

        current = audit.cross_validation.sac_validation_shape(self)
        prior = audit.cross_validation.sac_validation_shape(prior_obj)
        if current["sf_sac_sections"] != prior["sf_sac_sections"]:
            raise LateChangeError

        meta_fields = ("submitted_by", "date_created", "report_id", "audit_type")
        for field in meta_fields:
            if current["sf_sac_meta"][field] != prior["sf_sac_meta"][field]:
                raise LateChangeError

        return True

    def get_friendly_status(self) -> str:
        """Return the friendly version of submission_status."""
        return dict(self.STATUS_CHOICES)[self.submission_status]

    def get_statuses(self) -> type[STATUS]:
        """Return all possible statuses."""
        return STATUS

    # Constants:
    STATUS_CHOICES = (
        (STATUS.IN_PROGRESS, "In Progress"),
        (STATUS.FLAGGED_FOR_REMOVAL, "Flagged for Removal"),
        (STATUS.READY_FOR_CERTIFICATION, "Ready for Certification"),
        (STATUS.AUDITOR_CERTIFIED, "Auditor Certified"),
        (STATUS.AUDITEE_CERTIFIED, "Auditee Certified"),
        (STATUS.CERTIFIED, "Certified"),
        (STATUS.SUBMITTED, "Submitted"),
        (STATUS.DISSEMINATED, "Disseminated"),
    )

    USER_PROVIDED_ORGANIZATION_TYPE_CODE = (
        ("state", _("State")),
        ("local", _("Local Government")),
        ("tribal", _("Indian Tribe or Tribal Organization")),
        ("higher-ed", _("Institution of higher education (IHE)")),
        ("non-profit", _("Non-profit")),
        ("unknown", _("Unknown")),
        ("none", _("None of these (for example, for-profit")),
    )

    AUDIT_TYPE_CODES = (
        ("single-audit", _("Single Audit")),
        ("program-specific", _("Program-Specific Audit")),
    )

    AUDIT_PERIOD = (
        ("annual", _("Annual")),
        ("biennial", _("Biennial")),
        ("other", _("Other")),
    )

    # 0. Meta data
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)
    submission_status = models.CharField(
        default=STATUS.IN_PROGRESS, choices=STATUS_CHOICES
    )
    data_source = models.CharField(default="GSAFAC")

    # implement an array of tuples as two arrays since we can only have simple fields inside an array
    transition_name = ArrayField(
        models.CharField(max_length=40, choices=STATUS_CHOICES),
        default=list,
        size=None,
        blank=True,
        null=True,
    )
    transition_date = ArrayField(
        models.DateTimeField(),
        default=list,
        size=None,
        blank=True,
        null=True,
    )

    report_id = models.CharField(unique=True)

    # Q2 Type of Uniform Guidance Audit
    audit_type = models.CharField(
        max_length=20, choices=AUDIT_TYPE_CODES, blank=True, null=True
    )

    # General Information
    # The general information fields are currently specified in two places:
    #   - report_submission.forms.GeneralInformationForm
    #   - schemas.sections.GeneralInformation.schema.json
    general_information = models.JSONField(
        blank=True, null=True, validators=[validate_general_information_json]
    )

    audit_information = models.JSONField(
        blank=True, null=True, validators=[validate_audit_information_json]
    )

    # Federal Awards:
    federal_awards = models.JSONField(
        blank=True, null=True, validators=[validate_federal_award_json]
    )

    # Corrective Action Plan:
    corrective_action_plan = models.JSONField(
        blank=True, null=True, validators=[validate_corrective_action_plan_json]
    )

    # Findings Text:
    findings_text = models.JSONField(
        blank=True, null=True, validators=[validate_findings_text_json]
    )

    # Findings Uniform Guidance:
    findings_uniform_guidance = models.JSONField(
        blank=True, null=True, validators=[validate_findings_uniform_guidance_json]
    )

    # Additional UEIs:
    additional_ueis = models.JSONField(
        blank=True, null=True, validators=[validate_additional_ueis_json]
    )

    # Additional EINs:
    additional_eins = models.JSONField(
        blank=True, null=True, validators=[validate_additional_eins_json]
    )

    # Secondary Auditors:
    secondary_auditors = models.JSONField(
        blank=True, null=True, validators=[validate_secondary_auditors_json]
    )

    # Notes to SEFA:
    notes_to_sefa = models.JSONField(
        blank=True, null=True, validators=[validate_notes_to_sefa_json]
    )

    auditor_certification = models.JSONField(
        blank=True, null=True, validators=[validate_auditor_certification_json]
    )

    auditee_certification = models.JSONField(
        blank=True, null=True, validators=[validate_auditee_certification_json]
    )

    tribal_data_consent = models.JSONField(
        blank=True, null=True, validators=[validate_tribal_data_consent_json]
    )

    cognizant_agency = models.CharField(
        help_text="Agency assigned to this large submission. Computed when the submisson is finalized, but may be overridden",
        max_length=2,
        blank=True,
        null=True,
        verbose_name="Cog Agency",
    )
    oversight_agency = models.CharField(
        help_text="Agency assigned to this not so large submission. Computed when the submisson is finalized",
        max_length=2,
        blank=True,
        null=True,
        verbose_name="OSight Agency",
    )

    def validate_full(self):
        """
        Full validation, intended for use when the user indicates that the
        submission is finished.
        """
        cross_result = self.validate_cross()
        individual_result = self.validate_individually()
        full_result = {}

        if "errors" in cross_result:
            full_result = cross_result
            if "errors" in individual_result:
                full_result["errors"].extend(individual_result["errors"])
        elif "errors" in individual_result:
            full_result = individual_result

        return full_result

    def validate_cross(self):
        """
        This method should NOT be run as part of full_clean(), because we want
        to be able to save in-progress submissions.

        A stub method to represent the cross-sheet, “full” validation that we
        do once all the individual sections are complete and valid in
        themselves.
        """
        shaped_sac = audit.cross_validation.sac_validation_shape(self)
        try:
            sar = SingleAuditReportFile.objects.filter(sac_id=self.id).latest(
                "date_created"
            )
        except SingleAuditReportFile.DoesNotExist:
            sar = None
        validation_functions = audit.cross_validation.functions
        errors = list(
            chain.from_iterable(
                [func(shaped_sac, sar=sar) for func in validation_functions]
            )
        )
        if errors:
            return {"errors": errors, "data": shaped_sac}
        return {}

    def validate_individually(self):
        """
        Runs the individual workbook validations, returning generic errors as a
        list of strings. Ignores workbooks that haven't been uploaded yet.
        """
        errors = []
        result = {}

        for section, section_handlers in FORM_SECTION_HANDLERS.items():
            validation_method = section_handlers["validator"]
            section_name = section_handlers["field_name"]
            audit_data = getattr(self, section_name)

            try:
                validation_method(audit_data)
            except ValidationError as err:
                # err.error_list will be [] if the workbook wasn't uploaded yet
                if err.error_list:
                    errors.append(
                        {
                            "error": f"The {SECTION_NAMES[section_name].friendly} workbook contains validation errors and will need to be re-uploaded. This is likely caused by changes made to our validations in the time since it was originally uploaded."
                        }
                    )

        if errors:
            result = {"errors": errors}

        return result

    @property
    def is_auditee_certified(self):
        return self.submission_status in [
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ]

    @property
    def is_auditor_certified(self):
        return self.submission_status in [
            STATUS.AUDITEE_CERTIFIED,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.CERTIFIED,
        ]

    @property
    def is_submitted(self):
        return self.submission_status in [STATUS.DISSEMINATED]

    def get_transition_date(self, status):
        index = self.transition_name.index(status)
        if index >= 0:
            return self.transition_date[index]
        return None


def excel_file_path(instance, _filename):
    """
    We want the actual filename in the filesystem to be unique and determined
    by report_id and form_section--not the user-provided filename.
    """
    return f"excel/{instance.sac.report_id}--{instance.form_section}.xlsx"


class ExcelFile(models.Model):
    """
    Data model to track uploaded Excel files and associate them with SingleAuditChecklists
    """

    file = models.FileField(upload_to=excel_file_path, validators=[validate_excel_file])
    filename = models.CharField(max_length=255)
    form_section = models.CharField(max_length=255)
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.sac.submission_status != STATUS.IN_PROGRESS:
            raise LateChangeError("Attemtped Excel file upload")

        self.filename = f"{self.sac.report_id}--{self.form_section}.xlsx"

        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=self.sac, user=event_user, event=event_type
            )

        super().save(*args, **kwargs)


def single_audit_report_path(instance, _filename):
    """
    We want the actual filename in the filesystem to be unique and determined
    by report_id, not the user-provided filename.
    """
    base_path = "singleauditreport"
    report_id = instance.sac.report_id
    return f"{base_path}/{report_id}.pdf"


class SingleAuditReportFile(models.Model):
    """
    Data model to track uploaded Single Audit report PDFs and associate them
    with SingleAuditChecklists
    """

    file = models.FileField(
        upload_to=single_audit_report_path,
        validators=[validate_single_audit_report_file],
    )
    filename = models.CharField(max_length=255)
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    component_page_numbers = models.JSONField(
        blank=True, null=True, validators=[validate_component_page_numbers]
    )

    def save(self, *args, **kwargs):
        report_id = SingleAuditChecklist.objects.get(id=self.sac.id).report_id
        self.filename = f"{report_id}.pdf"
        if self.sac.submission_status != STATUS.IN_PROGRESS:
            raise LateChangeError("Attempted PDF upload")

        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=self.sac, user=event_user, event=event_type
            )

        super().save(*args, **kwargs)


class UeiValidationWaiver(models.Model):
    """Records of UEIs that are permitted to be inactive."""

    # Method overrides:
    def __str__(self):
        return f"#{self.id}--{self.uei}"

    # Not unique, in the case that one UEI needs to be waived several times with different expiration dates.
    uei = models.TextField("UEI")
    timestamp = models.DateTimeField(
        "When the waiver was created",
        default=django_timezone.now,
    )
    expiration = models.DateTimeField(
        "When the waiver will expire",
        default=one_month_from_today,
    )
    approver_email = models.TextField(
        "Email address of FAC staff member approving the waiver",
    )
    approver_name = models.TextField(
        "Name of FAC staff member approving the waiver",
    )
    requester_email = models.TextField(
        "Email address of NSAC/KSAML requesting the waiver",
    )
    requester_name = models.TextField(
        "Name of NSAC/KSAML requesting the waiver",
    )
    justification = models.TextField(
        "Brief plain-text justification for the waiver",
    )


class SacValidationWaiver(models.Model):
    """Records of reports that have had a requirement waived."""

    class TYPES:
        AUDITEE_CERTIFYING_OFFICIAL = "auditee_certifying_official"
        AUDITOR_CERTIFYING_OFFICIAL = "auditor_certifying_official"
        FINDING_REFERENCE_NUMBER = "finding_reference_number"
        PRIOR_REFERENCES = "prior_references"

    WAIVER_CHOICES = [
        (
            TYPES.AUDITEE_CERTIFYING_OFFICIAL,
            "No auditee certifying official is available",
        ),
        (
            TYPES.AUDITOR_CERTIFYING_OFFICIAL,
            "No auditor certifying official is available",
        ),
        (
            TYPES.FINDING_REFERENCE_NUMBER,
            "Report has duplicate finding reference numbers",
        ),
        (
            TYPES.PRIOR_REFERENCES,
            "Report has invalid prior reference numbers",
        ),
    ]
    report_id = models.ForeignKey(
        "SingleAuditChecklist",
        help_text="The report that the waiver applies to",
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    timestamp = models.DateTimeField(
        "When the waiver was created",
        default=django_timezone.now,
    )
    approver_email = models.TextField(
        "Email address of FAC staff member approving the waiver",
    )
    approver_name = models.TextField(
        "Name of FAC staff member approving the waiver",
    )
    requester_email = models.TextField(
        "Email address of NSAC/KSAML requesting the waiver",
    )
    requester_name = models.TextField(
        "Name of NSAC/KSAML requesting the waiver",
    )
    justification = models.TextField(
        "Brief plain-text justification for the waiver",
    )
    waiver_types = ArrayField(
        models.CharField(
            max_length=50,
            choices=WAIVER_CHOICES,
        ),
        verbose_name="The waiver type",
        default=list,
    )
