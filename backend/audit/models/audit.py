from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Field, GeneratedField, Transform
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast

from audit.cross_validation.naming import SECTION_NAMES
from audit.cross_validation.audit_validation_shape import audit_validation_shape
from audit.models import SingleAuditReportFile
from audit.models.constants import (
    AUDIT_TYPE_CODES,
    STATUS,
    STATUS_CHOICES,
    EventType,
    AUDIT_SEQUENCE_ID,
)
from audit.models.history import History
from audit.models.mixins import CreatedMixin, UpdatedMixin
from audit.models.utils import (
    get_next_sequence_id,
    generate_sac_report_id,
    JsonArrayToTextArray,
    validate_audit_consistency,
)

from itertools import chain
from audit.cross_validation import functions as cross_validation_functions
from audit.utils import FORM_SECTION_HANDLERS
import logging
import time

User = get_user_model()
logger = logging.getLogger(__name__)


class AuditManager(models.Manager):
    """
    Custom Manager for Audits. Creating an audit will generate the report_id.
    """

    def create(self, **obj_data):
        user = obj_data.pop("event_user")
        event_type = obj_data.pop("event_type")
        created_by = obj_data.pop("created_by") if "created_by" in obj_data else user
        end_date = obj_data["audit"]["general_information"]["auditee_fiscal_period_end"]

        # TODO: SoT
        # Re-consider this. We moved the report_id generation into the transaction.
        with transaction.atomic():

            # We do not want the else condition to pass until we deprecate the SAC.
            # This is so that the report_ids stay consistent between SAC and Audit.
            if "report_id" in obj_data:
                report_id = obj_data.pop("report_id")
            else:
                report_id = generate_sac_report_id(
                    sequence=get_next_sequence_id(AUDIT_SEQUENCE_ID),
                    end_date=end_date,
                )
            version = 0

            # TODO: SoT
            # Once we deprecate the SAC, we need to pass the "id" here, which will = sequence.
            # This prevents id sequencing from incrementing by 2.
            updated = obj_data | {
                "report_id": report_id,
                "version": version,
                "created_by": created_by,
                "updated_by": user,
            }

            result = super().create(**updated)
            History.objects.create(
                event=event_type,
                report_id=report_id,
                version=version,
                event_data=result.audit,
                updated_by=user,
            )
            return result

    def get_current_version(self, report_id):
        """Returns the current version of the audit."""
        try:
            # Note: This will need to change if we pivot to using a combined key
            audit = self.get(report_id=report_id)
            return audit.version
        except self.model.DoesNotExist:
            return 0

    # TODO: Update Post SOC Launch Delete
    def find_audit_or_none(self, report_id):
        """This is a temporary helper method to pass linting for too complex methods"""
        try:
            return self.get(report_id=report_id)
        except Audit.DoesNotExist:
            return None


class Audit(CreatedMixin, UpdatedMixin):
    """
    Model object representing the audit. The audit is mutable up until it is submitted.
    After the Audit is submitted, it should be considered immutable. Versioning is
    there to track changes during the submission flow, and to allow the creation of a
    re-submission, while preserving the 'old' audit.
    """

    submission_status = models.CharField(
        default=STATUS.IN_PROGRESS, choices=STATUS_CHOICES
    )
    report_id = models.CharField(unique=True)
    version = models.IntegerField()
    audit_type = models.CharField(
        max_length=20, choices=AUDIT_TYPE_CODES, blank=True, null=True
    )
    data_source = models.CharField(default="GSAFAC")
    audit = models.JSONField()

    # All the Generated Fields are used to improve search performance.
    findings_summary = GeneratedField(
        expression=Cast(
            KeyTextTransform(
                "findings_summary", KeyTextTransform("search_indexes", "audit")
            ),
            output_field=models.IntegerField(),
        ),
        output_field=models.IntegerField(),
        db_persist=True,
    )

    audit_year = GeneratedField(
        expression=Cast(
            KeyTextTransform("audit_year", "audit"), output_field=models.IntegerField()
        ),
        output_field=models.IntegerField(),
        db_persist=True,
    )

    auditee_state = GeneratedField(
        expression=KeyTextTransform(
            "auditee_state", KeyTextTransform("general_information", "audit")
        ),
        output_field=models.CharField(),
        db_persist=True,
    )

    fac_accepted_date = GeneratedField(
        expression=KeyTextTransform("fac_accepted_date", "audit"),
        output_field=models.CharField(),
        db_persist=True,
    )

    fy_end_month = GeneratedField(
        expression=Cast(
            KeyTextTransform("fy_end_month", "audit"),
            output_field=models.IntegerField(),
        ),
        output_field=models.IntegerField(),
        db_persist=True,
    )

    organization_type = GeneratedField(
        expression=KeyTextTransform(
            "user_provided_organization_type",
            KeyTextTransform("general_information", "audit"),
        ),
        output_field=models.CharField(),
        db_persist=True,
    )

    is_public = GeneratedField(
        expression=Cast(
            KeyTextTransform("is_public", "audit"), output_field=models.BooleanField()
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    cognizant_agency = GeneratedField(
        expression=KeyTextTransform("cognizant_agency", "audit"),
        output_field=models.CharField(),
        db_persist=True,
    )

    oversight_agency = GeneratedField(
        expression=KeyTextTransform("oversight_agency", "audit"),
        output_field=models.CharField(),
        db_persist=True,
    )

    has_direct_funding = GeneratedField(
        expression=Cast(
            KeyTextTransform(
                "has_direct_funding", KeyTextTransform("search_indexes", "audit")
            ),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    has_indirect_funding = GeneratedField(
        expression=Cast(
            KeyTextTransform(
                "has_indirect_funding", KeyTextTransform("search_indexes", "audit")
            ),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    is_major_program = GeneratedField(
        expression=Cast(
            KeyTextTransform(
                "is_major_program", KeyTextTransform("search_indexes", "audit")
            ),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )

    program_names = GeneratedField(
        expression=JsonArrayToTextArray("audit__search_indexes__program_names"),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    additional_ueis = GeneratedField(
        expression=JsonArrayToTextArray("audit__additional_ueis"),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    additional_eins = GeneratedField(
        expression=JsonArrayToTextArray("audit__additional_eins"),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    auditee_uei = GeneratedField(
        expression=KeyTextTransform(
            "auditee_uei", KeyTextTransform("general_information", "audit")
        ),
        output_field=models.CharField(),
        db_persist=True,
    )

    auditee_ein = GeneratedField(
        expression=KeyTextTransform(
            "ein", KeyTextTransform("general_information", "audit")
        ),
        output_field=models.CharField(),
        db_persist=True,
    )

    passthrough_names = GeneratedField(
        expression=JsonArrayToTextArray("audit__search_indexes__passthrough_names"),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    search_names = GeneratedField(
        expression=JsonArrayToTextArray("audit__search_indexes__search_names"),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    agency_extensions = GeneratedField(
        expression=JsonArrayToTextArray("audit__search_indexes__agency_extensions"),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    agency_prefixes = GeneratedField(
        expression=JsonArrayToTextArray("audit__search_indexes__agency_prefixes"),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    compliance_requirements = GeneratedField(
        expression=JsonArrayToTextArray(
            "audit__search_indexes__compliance_requirements"
        ),
        output_field=ArrayField(models.CharField()),
        db_persist=True,
    )

    auditee_name = GeneratedField(
        expression=KeyTextTransform(
            "auditee_name", KeyTextTransform("general_information", "audit")
        ),
        output_field=models.CharField(),
        db_persist=True,
    )

    objects = AuditManager()

    @property
    def submitted_by(self):
        history = (
            History.objects.filter(report_id=self.report_id, event=EventType.SUBMITTED)
            .order_by("-updated_at")
            .first()
        )
        return history.updated_by if history else None

    @property
    def auditee_fiscal_period_end(self):
        return self.audit.get("general_information", {}).get(
            "auditee_fiscal_period_end"
        )

    class Meta:
        # Uncomment this line should we decide to make disseminated reports immutable in resubmission
        # unique_together = ("report_id", "version")
        # Admin View
        verbose_name = "Audit"
        verbose_name_plural = "Audits"

    def save(self, *args, **kwargs):
        """
        Overriding the save method to add an entry to history table and conditional save.
        """
        event_user = kwargs.get("event_user")
        event_type = kwargs.get("event_type")
        report_id = self.report_id
        previous_version = self.version

        self.updated_by = self.updated_by if self.updated_by else event_user

        with transaction.atomic():
            current_version = Audit.objects.get_current_version(report_id)
            if previous_version != current_version:
                logger.error(
                    f"Version Mismatch: Expected {previous_version} Got {current_version}"
                )  # TODO

            # TESTING: During save of audit, check for matching data in SAC
            logger.info(f"Validating {report_id}")
            t0 = time.time()
            is_consistent, discrepancies = validate_audit_consistency(self)
            t1 = time.time()
            logger.info(f"-- {t1 - t0}s")

            if not is_consistent:
                logger.warning(
                    f"Inconsistencies found between models for {report_id}: {discrepancies}"
                )

            self.version = previous_version + 1

            if event_type and event_user:
                History.objects.create(
                    event=event_type,
                    report_id=report_id,
                    version=self.version,
                    event_data=self.audit,
                    updated_by=self.updated_by,
                )
            return super().save()

    def validate(self):
        """
        Full validation, intended for use when the user indicates that the
        submission is finished.
        """
        cross_result = self._validate_cross()
        individual_result = self._validate_individually()
        full_result = {}

        if "errors" in cross_result:
            full_result = cross_result
            if "errors" in individual_result:
                full_result["errors"].extend(individual_result["errors"])
        elif "errors" in individual_result:
            full_result = individual_result

        return full_result

    def _validate_individually(self):
        """
        Runs the individual workbook validations, returning generic errors as a
        list of strings. Ignores workbooks that haven't been uploaded yet.
        """
        errors = []
        result = {}

        for section, section_handlers in FORM_SECTION_HANDLERS.items():
            validation_method = section_handlers["validator"]
            section_name = section_handlers["field_name"]
            audit_data = self.audit.get(section_name, {})

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

    def _validate_cross(self):
        """
        This method should NOT be run as part of full_clean(), because we want
        to be able to save in-progress submissions.

        A stub method to represent the cross-sheet, “full” validation that we
        do once all the individual sections are complete and valid in
        themselves.
        """
        shaped_audit = audit_validation_shape(self)
        try:
            sar = SingleAuditReportFile.objects.filter(sac_id=self.id).latest(
                "date_created"
            )
        except SingleAuditReportFile.DoesNotExist:
            sar = None

        errors = list(
            chain.from_iterable(
                [func(shaped_audit, sar=sar) for func in cross_validation_functions]
            )
        )
        if errors:
            return {"errors": errors, "data": shaped_audit}
        return {}

    @Field.register_lookup
    class DateCast(Transform):
        lookup_name = "date"
        bilateral = True

        def as_sql(self, compiler, connection, **kwargs):
            sql, params = compiler.compile(self.lhs)
            sql = "CAST(%s AS DATE)" % sql
            return sql, params
