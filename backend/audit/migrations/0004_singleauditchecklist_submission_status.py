# Generated by Django 4.0.4 on 2022-06-08 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "audit",
            "0003_rename_auditor_name_singleauditchecklist_auditor_firm_name_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="singleauditchecklist",
            name="submission_status",
            field=models.CharField(
                choices=[
                    ("in_progress", "In progress"),
                    ("submitted", "Submitted"),
                    ("received", "Received"),
                    ("available", "Available"),
                ],
                default="in_progress",
                max_length=16,
            ),
        ),
    ]
