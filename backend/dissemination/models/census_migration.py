from django.db import models
from django.utils import timezone


class MigrationInspectionRecord(models.Model):
    audit_year = models.TextField(blank=True, null=True)
    dbkey = models.TextField(blank=True, null=True)
    report_id = models.TextField(blank=True, null=True)
    run_datetime = models.DateTimeField(default=timezone.now)
    finding_text = models.JSONField(blank=True, null=True)
    additional_uei = models.JSONField(blank=True, null=True)
    additional_ein = models.JSONField(blank=True, null=True)
    finding = models.JSONField(blank=True, null=True)
    federal_award = models.JSONField(blank=True, null=True)
    cap_text = models.JSONField(blank=True, null=True)
    note = models.JSONField(blank=True, null=True)
    passthrough = models.JSONField(blank=True, null=True)
    general = models.JSONField(blank=True, null=True)
    secondary_auditor = models.JSONField(blank=True, null=True)


class InvalidAuditRecord(models.Model):
    """Model holds records that have been migrated as is, without validation or changes."""

    audit_year = models.TextField(blank=True, null=True)
    dbkey = models.TextField(blank=True, null=True)
    report_id = models.TextField(blank=True, null=True)
    run_datetime = models.DateTimeField(default=timezone.now)
    finding_text = models.JSONField(blank=True, null=True)
    additional_uei = models.JSONField(blank=True, null=True)
    additional_ein = models.JSONField(blank=True, null=True)
    finding = models.JSONField(blank=True, null=True)
    federal_award = models.JSONField(blank=True, null=True)
    cap_text = models.JSONField(blank=True, null=True)
    note = models.JSONField(blank=True, null=True)
    passthrough = models.JSONField(blank=True, null=True)
    general = models.JSONField(blank=True, null=True)
    secondary_auditor = models.JSONField(blank=True, null=True)


class IssueDescriptionRecord(models.Model):
    """Issue descriptions for unvalidated audit records."""

    issue_detail = models.TextField()
    issue_tag = models.TextField()
    skipped_validation_method = models.TextField()
