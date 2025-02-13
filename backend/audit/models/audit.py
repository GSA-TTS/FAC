import logging

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import GeneratedField, Field, Transform, F, Func
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast

from audit.models.constants import AUDIT_TYPE_CODES, STATUS, STATUS_CHOICES
from audit.models.history import History
from audit.models.schema import Schema
from audit.models.utils import generate_sac_report_id

logger = logging.getLogger(__name__)

class JsonArrayToTextArray(Func):
    function = 'json_array_to_text_array'
    output_field = ArrayField(models.CharField())

User = get_user_model()
class AuditManager(models.Manager):
    """
    Custom Manager for Audits. Creating an audit will generate the report_id.
    """
    def create(self, **obj_data):
        user = obj_data.pop("event_user")
        event_type = obj_data.pop("event_type")
        end_date = obj_data["audit"]["general_information"]["auditee_fiscal_period_end"]
        report_id = obj_data.pop("report_id") if obj_data["report_id"] \
            else generate_sac_report_id(count=self.model.objects.count(),
                                        end_date=end_date) #TODO -> May want to adjust this
        version = 0

        updated = obj_data | {"report_id": report_id, "version": version, "created_by": user, "updated_by": user}
        with transaction.atomic():
            result = super().create(**updated)
            History.objects.create(event=event_type,
                                   report_id=report_id,
                                   version=version,
                                   audit=result.audit,
                                   updated_by=user)
            return result

    def get_current_version(self, report_id):
        """Returns the current version of the audit."""
        try:
            audit = self.get(report_id=report_id)
            # Confirm Audit Exists?
            return audit.version
        except self.model.DoesNotExist:
            return 0

class Audit(models.Model):
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
    schema = models.ForeignKey(Schema, on_delete=models.PROTECT, related_name="+")
    data_source = models.CharField(default="GSAFAC")
    audit = models.JSONField()

    # Basic auditing of the audit (see what we did there?)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    # All the Generated Fields are used to improve search performance.
    findings_summary = GeneratedField(
        expression=Cast(KeyTextTransform('findings_summary', KeyTextTransform('search_indexes', 'audit')), output_field=models.IntegerField()),
        output_field=models.IntegerField(),
        db_persist=True
    )

    audit_year = GeneratedField(
        expression=Cast(KeyTextTransform('audit_year', 'audit'), output_field=models.IntegerField()),
        output_field=models.IntegerField(),
        db_persist=True
    )

    auditee_state = GeneratedField(
        expression=KeyTextTransform('auditee_state', KeyTextTransform('general_information', 'audit')),
        output_field=models.CharField(), # TODO: Determine max_length
        db_persist=True
    )

    fac_accepted_date = GeneratedField(
        expression=KeyTextTransform('fac_accepted_date', 'audit'),
        output_field=models.CharField(),
        db_persist=True
    )

    fy_end_month = GeneratedField(
        expression=Cast(KeyTextTransform('fy_end_month', 'audit'), output_field=models.IntegerField()),
        output_field=models.IntegerField(),
        db_persist=True
    )

    organization_type = GeneratedField(
        expression=KeyTextTransform('user_provided_organization_type', KeyTextTransform('general_information', 'audit')),
        output_field=models.CharField(),
        db_persist=True
    )

    is_public = GeneratedField(
        expression=Cast(KeyTextTransform('is_public', 'audit'), output_field=models.BooleanField()),
        output_field=models.BooleanField(),
        db_persist=True
    )

    cognizant_agency = GeneratedField(
        expression=KeyTextTransform('cognizant_agency', 'audit'),
        output_field=models.CharField(),
        db_persist=True
    )

    oversight_agency = GeneratedField(
        expression=KeyTextTransform('oversight_agency', 'audit'),
        output_field=models.CharField(),
        db_persist=True
    )

    has_direct_funding = GeneratedField(
        expression=Cast(KeyTextTransform('has_direct_funding', KeyTextTransform('search_indexes', 'audit')), output_field=models.BooleanField()),
        output_field=models.BooleanField(),
        db_persist=True
    )

    has_indirect_funding = GeneratedField(
        expression=Cast(KeyTextTransform('has_indirect_funding', KeyTextTransform('search_indexes', 'audit')),
                        output_field=models.BooleanField()),
        output_field=models.BooleanField(),
        db_persist=True
    )

    is_major_program = GeneratedField(
        expression=Cast(KeyTextTransform('is_major_program', KeyTextTransform('search_indexes', 'audit')), output_field=models.BooleanField()),
        output_field=models.BooleanField(),
        db_persist=True
    )

    program_names = GeneratedField(
        expression=JsonArrayToTextArray('audit__search_indexes__program_names'),
        output_field=ArrayField(models.CharField()),
        db_persist=True
    )

    additional_ueis = GeneratedField(
        expression=JsonArrayToTextArray('audit__additional_ueis'),
        output_field=ArrayField(models.CharField()),
        db_persist=True
    )

    additional_eins = GeneratedField(
        expression=JsonArrayToTextArray('audit__additional_eins'),
        output_field=ArrayField(models.CharField()),
        db_persist=True
    )

    auditee_uei = GeneratedField(
        expression=KeyTextTransform('auditee_uei', KeyTextTransform('general_information', 'audit')),
        output_field=models.CharField(),
        db_persist=True
    )

    auditee_ein = GeneratedField(
        expression=KeyTextTransform('auditee_ein',
                                    KeyTextTransform('general_information', 'audit')),
        output_field=models.CharField(),
        db_persist=True
    )

    passthrough_names = GeneratedField(
        expression=JsonArrayToTextArray('audit__search_indexes__passthrough_names'),
        output_field=ArrayField(models.CharField()),
        db_persist=True
    )

    search_names = GeneratedField(
        expression=JsonArrayToTextArray('audit__search_indexes__search_names'),
        output_field=ArrayField(models.CharField()),
        db_persist=True
    )

    agency_extensions = GeneratedField(
        expression=JsonArrayToTextArray('audit__search_indexes__agency_extensions'),
        output_field=ArrayField(models.CharField()),
        db_persist=True
    )

    agency_prefixes = GeneratedField(
        expression=JsonArrayToTextArray('audit__search_indexes__agency_prefixes'),
        output_field=ArrayField(models.CharField()),
        db_persist=True
    )
    objects = AuditManager()

    class Meta:
        # unique_together = ("report_id", "version") # TODO: Decide!
        # Admin View
        verbose_name = "SF-SAC"
        verbose_name_plural = "SF-SACs"

    def save(self, *args, **kwargs):
        """
        Overriding the save method to add an entry to history table and conditional save.
        """
        event_user = kwargs.get("event_user")
        event_type = kwargs.get("event_type")
        report_id = self.report_id
        previous_version = self.version

        self.updated_by = self.updated_by if self.updated_by else event_user
        self.version = previous_version + 1

        with transaction.atomic():
            current_version = Audit.objects.get_current_version(report_id)
            if previous_version != current_version:
                raise Exception(f"Version Mismatch: Expected {previous_version} Got {current_version}") # TODO

            if event_type and event_user:
                History.objects.create(event=event_type,
                                       report_id=report_id,
                                       version=self.version,
                                       audit=self.audit,
                                       updated_by=self.updated_by)
            return super().save()

    @Field.register_lookup
    class DateCast(Transform):
        # Register this before you filter things, for example in models.py
        lookup_name = 'date'  # Used as object.filter(LeftField__int__gte, "777")
        bilateral = True  # To cast both left and right

        def as_sql(self, compiler, connection):
            sql, params = compiler.compile(self.lhs)
            sql = 'CAST(%s AS DATE)' % sql
            return sql, params


