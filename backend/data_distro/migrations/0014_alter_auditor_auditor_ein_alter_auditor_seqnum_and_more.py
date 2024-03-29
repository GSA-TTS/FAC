# Generated by Django 4.1.4 on 2023-02-10 20:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_distro", "0013_alter_auditee_duns_list"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditor",
            name="auditor_ein",
            field=models.IntegerField(
                help_text="Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN (AND) Data sources: SF-SAC 2013-2015: I/8/b; SF-SAC 2016-2018: I/8/b; SF-SAC 2019-2021: I/6/h/ii; SF-SAC 2022: I/6/h/ii Census mapping: MULTIPLE CPAS INFO, CPAEIN",
                null=True,
                verbose_name="CPA Firm EIN (only available for audit years 2013 and beyond)",
            ),
        ),
        migrations.AlterField(
            model_name="auditor",
            name="seqnum",
            field=models.IntegerField(
                help_text="Census mapping: GENERAL, SEQNUM (AND) Census mapping: MULTIPLE CPAS INFO, SEQNUM",
                null=True,
                verbose_name="Order that Auditors were reported on page 5 of SF-SAC",
            ),
        ),
        migrations.AlterField(
            model_name="general",
            name="condition_or_deficiency_major_program",
            field=models.BooleanField(
                help_text="Data sources: SF-SAC 2001-2003: III/5; SF-SAC 2004-2007: III/4; SF-SAC 2008-2009: III/4; SF-SAC 2010-2012: III/4 Census mapping: GENERAL, REPORTABLECONDITION_MP",
                null=True,
                verbose_name="Whether or not the audit disclosed a reportable condition/significant deficiency for any major program in the Schedule of Findings and Questioned Costs",
            ),
        ),
    ]
