# Generated by Django 5.0.2 on 2024-05-16 20:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dissemination", "0015_disseminationcombined"),
    ]

    operations = [
        migrations.CreateModel(
            name="InvalidAuditRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("audit_year", models.TextField(blank=True, null=True)),
                ("dbkey", models.TextField(blank=True, null=True)),
                ("report_id", models.TextField(blank=True, null=True)),
                (
                    "run_datetime",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("finding_text", models.JSONField(blank=True, null=True)),
                ("additional_uei", models.JSONField(blank=True, null=True)),
                ("additional_ein", models.JSONField(blank=True, null=True)),
                ("finding", models.JSONField(blank=True, null=True)),
                ("federal_award", models.JSONField(blank=True, null=True)),
                ("cap_text", models.JSONField(blank=True, null=True)),
                ("note", models.JSONField(blank=True, null=True)),
                ("passthrough", models.JSONField(blank=True, null=True)),
                ("general", models.JSONField(blank=True, null=True)),
                ("secondary_auditor", models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="IssueDescriptionRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("issue_detail", models.TextField()),
                ("issue_tag", models.TextField()),
                ("skipped_validation_method", models.TextField()),
            ],
        ),
    ]