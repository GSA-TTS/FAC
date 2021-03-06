# Generated by Django 4.0.4 on 2022-07-20 23:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0007_alter_singleauditchecklist_auditee_uei"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="access",
            options={"verbose_name_plural": "accesses"},
        ),
        migrations.RenameField(
            model_name="access",
            old_name="user_id",
            new_name="user",
        ),
        migrations.RemoveField(
            model_name="access",
            name="sac",
        ),
        migrations.AddField(
            model_name="singleauditchecklist",
            name="auditee_contacts",
            field=models.ManyToManyField(
                null=True,
                related_name="auditee_contacts",
                to="audit.access",
                verbose_name="list of auditees with access",
            ),
        ),
        migrations.AddField(
            model_name="singleauditchecklist",
            name="auditor_contacts",
            field=models.ManyToManyField(
                null=True,
                related_name="auditor_contacts",
                to="audit.access",
                verbose_name="list of auditors with access",
            ),
        ),
        migrations.AddField(
            model_name="singleauditchecklist",
            name="certifying_auditee_contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="certifying_auditee_contact",
                to="audit.access",
            ),
        ),
        migrations.AddField(
            model_name="singleauditchecklist",
            name="certifying_auditor_contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="certifying_auditor_contact",
                to="audit.access",
            ),
        ),
    ]
