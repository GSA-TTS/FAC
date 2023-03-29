"""
This step needs to be run after a migration so that there are not concurrent locks on a table.


"""
from io import StringIO

from django.db import migrations
from django.core.management import call_command


def update_docs_and_views(apps, schema_editor):
    """Runs our management command to add documentation to sql"""
    call_command(
        "create_docs",
        stdout="",
        stderr=StringIO(),
    )

    # Recreating the API views where the names were updated
    call_command(
        "create_distro_api",
        stdout="",
        stderr=StringIO(),
        **{"file": "sql_migrations/002_basic_views.sql"},
    )

    call_command(
        "create_distro_api",
        stdout="",
        stderr=StringIO(),
        **{"file": "sql_migrations/003_findings.sql"},
    )

    # Adding high-level docs for the views
    call_command(
        "create_distro_api",
        stdout="",
        stderr=StringIO(),
        **{"file": "sql_migrations/005_docs_for_views.sql"},
    )


class Migration(migrations.Migration):
    dependencies = [
        ("data_distro", "0031_rename_seqence_number_to_sequence_number"),
    ]

    operations = [migrations.RunPython(update_docs_and_views)]
