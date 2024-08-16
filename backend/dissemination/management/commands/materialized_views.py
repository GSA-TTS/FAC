from django.core.management.base import BaseCommand
from dissemination import api_versions


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate access tables for the postgrest API.
    """

    def add_arguments(self, parser):
        parser.add_argument("-c", "--create", action="store_true", default=False)
        parser.add_argument("-d", "--drop", action="store_true", default=False)
        parser.add_argument("-r", "--refresh", action="store_true", default=False)

    def handle(self, *args, **options):
        path = "dissemination/sql"
        if options["create"]:
            # Other API views may rely on the materialized view. So, drop and recreate them.
            api_versions.drop_live_views("dissemination")
            api_versions.exec_sql_at_path(path, "create_materialized_views.sql")
            api_versions.create_live_views("dissemination")
        elif options["drop"]:
            api_versions.exec_sql_at_path(path, "drop_materialized_views.sql")
        elif options["refresh"]:
            api_versions.exec_sql_at_path(path, "refresh_materialized_views.sql")
