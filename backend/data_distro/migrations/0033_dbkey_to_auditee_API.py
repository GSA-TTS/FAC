"""
This step needs to be run after a migration so that there are not concurrent locks on a table.


"""
from io import StringIO

from django.db import migrations
from django.core.management import call_command


def update_view(apps, schema_editor):
    """Runs our management command to add documentation to sql"""

    # Adding DBKEY to auditee view
    call_command(
        "create_distro_api",
        stdout="",
        stderr=StringIO(),
        **{"file": "sql_migrations/006_dbkey_for_auditee.sql"},
    )


class Migration(migrations.Migration):
    dependencies = [
        ("data_distro", "0032_update_API"),
    ]

    operations = [migrations.RunPython(update_view)]
