from django.core.management.base import BaseCommand
from dissemination import api_versions


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate access tables for the postgrest API.
    """

    def handle(self, *args, **kwargs):
        api_versions.create_access_tables("support")
