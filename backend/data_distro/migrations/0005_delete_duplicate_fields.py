"""
In the last migration we added the fields we were moving to their new classes. This deletes the old fields that are no longer needed.
"""

# Generated by Django 4.1.4 on 2023-01-26 11:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_distro", "0004_add_new_models"),
    ]

    operations = [
        migrations.DeleteModel(
            name="DunsInfo",
        ),
        migrations.DeleteModel(
            name="EinInfo",
        ),
        migrations.DeleteModel(
            name="MultipleCpasInfo",
        ),
        migrations.DeleteModel(
            name="UeiInfo",
        ),
        migrations.RemoveField(
            model_name="auditor",
            name="audit_year",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_certify_name",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_certify_title",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_contact",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_email",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_fax",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_name",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_name_title",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_phone",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditee_title",
        ),
        migrations.RemoveField(
            model_name="general",
            name="auditor_ein",
        ),
        migrations.RemoveField(
            model_name="general",
            name="city",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_city",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_contact",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_country",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_email",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_fax",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_firm_name",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_foreign",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_phone",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_state",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_street1",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_street2",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_title",
        ),
        migrations.RemoveField(
            model_name="general",
            name="cpa_zip_code",
        ),
        migrations.RemoveField(
            model_name="general",
            name="duns",
        ),
        migrations.RemoveField(
            model_name="general",
            name="ein",
        ),
        migrations.RemoveField(
            model_name="general",
            name="ein_subcode",
        ),
        migrations.RemoveField(
            model_name="general",
            name="multiple_cpas",
        ),
        migrations.RemoveField(
            model_name="general",
            name="multiple_duns",
        ),
        migrations.RemoveField(
            model_name="general",
            name="multiple_eins",
        ),
        migrations.RemoveField(
            model_name="general",
            name="multiple_ueis",
        ),
        migrations.RemoveField(
            model_name="general",
            name="state",
        ),
        migrations.RemoveField(
            model_name="general",
            name="street1",
        ),
        migrations.RemoveField(
            model_name="general",
            name="street2",
        ),
        migrations.RemoveField(
            model_name="general",
            name="uei",
        ),
        migrations.RemoveField(
            model_name="general",
            name="zip_code",
        ),
        migrations.AddField(
            model_name="auditee",
            name="ein",
            field=models.IntegerField(
                default=0,
                help_text="Data sources: SF-SAC 1997-2000: I/5/a; SF-SAC 2001-2003: I/5/a; SF-SAC 2004-2007: I/5/a; SF-SAC 2008-2009: I/4/a; SF-SAC 2010-2012: I/4/a; SF-SAC 2013-2015: I/4/a; SF-SAC 2016-2018: I/4/a; SF-SAC 2019-2021: I/4/a; SF-SAC 2022: I/4/a Census mapping: GENERAL, EIN",
                verbose_name="Primary Employer Identification Number",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="auditee",
            name="ein_subcode",
            field=models.IntegerField(
                help_text="Census mapping: GENERAL, EINSUBCODE",
                null=True,
                verbose_name="Subcode assigned to the EIN",
            ),
        ),
        migrations.AddField(
            model_name="auditor",
            name="auditor_ein",
            field=models.IntegerField(
                default=0,
                help_text="Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN",
                verbose_name="CPA Firm EIN (only available for audit years 2013 and beyond)",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="auditor",
            name="cpa_country",
            field=models.CharField(
                help_text="Data sources: SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPACOUNTRY",
                max_length=6,
                null=True,
                verbose_name="CPA Country",
            ),
        ),
        migrations.AddField(
            model_name="auditor",
            name="cpa_foreign",
            field=models.CharField(
                help_text="Data sources: SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPAFOREIGN",
                max_length=200,
                null=True,
                verbose_name="CPA Address - if international",
            ),
        ),
        migrations.AlterField(
            model_name="auditee",
            name="zip_code",
            field=models.CharField(
                help_text="Data sources: SF-SAC 1997-2000: I/6/b; SF-SAC 2001-2003: I/6/b; SF-SAC 2004-2007: I/6/b; SF-SAC 2008-2009: I/5/b; SF-SAC 2010-2012: I/5/b; SF-SAC 2013-2015: I/5/b; SF-SAC 2016-2018: I/5/b; SF-SAC 2019-2021: I/5/b; SF-SAC 2022: I/5/b Census mapping: GENERAL, ZIPCODE",
                max_length=12,
                verbose_name="Auditee Zip Code",
            ),
        ),
        migrations.AlterField(
            model_name="auditor",
            name="cpa_zip_code",
            field=models.CharField(
                help_text="Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/f; SF-SAC 2016-2018: I/8/f; SF-SAC 2019-2021: I/6/h/vi; SF-SAC 2022: I/6/h/vi Census mapping: MULTIPLE CPAS INFO, CPAZIPCODE",
                max_length=12,
                null=True,
                verbose_name="CPA Zip Code",
            ),
        ),
    ]
