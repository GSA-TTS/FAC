# Generated by Django 4.2.6 on 2024-01-09 01:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("dissemination", "0009_alter_general_auditor_certify_name_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="MigrationChangeRecord",
            new_name="MigrationInspectionRecord",
        ),
    ]