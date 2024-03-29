# Generated by Django 4.1.4 on 2023-02-13 15:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_distro", "0014_alter_auditor_auditor_ein_alter_auditor_seqnum_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="auditee",
            old_name="city",
            new_name="auditee_city",
        ),
        migrations.RenameField(
            model_name="auditee",
            old_name="state",
            new_name="auditee_state",
        ),
        migrations.RenameField(
            model_name="auditee",
            old_name="street1",
            new_name="auditee_street1",
        ),
        migrations.RenameField(
            model_name="auditee",
            old_name="street2",
            new_name="auditee_street2",
        ),
        migrations.AlterField(
            model_name="auditor",
            name="cpa_ein",
            field=models.IntegerField(
                help_text="Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN (AND) Data sources: SF-SAC 2013-2015: I/8/b; SF-SAC 2016-2018: I/8/b; SF-SAC 2019-2021: I/6/h/ii; SF-SAC 2022: I/6/h/ii Census mapping: MULTIPLE CPAS INFO, CPAEIN",
                null=True,
                verbose_name="CPA Firm EIN (only available for audit years 2013 and beyond)",
            ),
        ),
        migrations.AlterField(
            model_name="cfdainfo",
            name="auditor_ein",
            field=models.IntegerField(
                help_text="Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN (AND) Data sources: SF-SAC 2013-2015: I/8/b; SF-SAC 2016-2018: I/8/b; SF-SAC 2019-2021: I/6/h/ii; SF-SAC 2022: I/6/h/ii Census mapping: MULTIPLE CPAS INFO, CPAEIN",
                null=True,
                verbose_name="Primary Employer Identification Number",
            ),
        ),
    ]
