from io import StringIO

from django.db import migrations
from django.core.management import call_command


def update_view(apps, schema_editor):
    """Runs our management command to add documentation to sql"""

    # Making views available to Postgrest API
    call_command(
        "create_distro_api",
        stdout="",
        stderr=StringIO(),
        **{"file": "sql_migrations/007_add_postgrest_notify.sql"},
    )

    # Adding column docs for the views
    call_command(
        "create_docs",
        stdout="",
        stderr=StringIO(),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("data_distro", "0033_dbkey_to_auditee_API"),
    ]

    operations = [migrations.RunPython(update_view)]
