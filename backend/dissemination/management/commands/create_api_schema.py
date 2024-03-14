from django.core.management.base import BaseCommand
from dissemination import api_versions


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate views for the postgrest API.
    """

    def handle(self, *args, **kwargs):
        api_versions.drop_live_schema("dissemination")
        api_versions.create_live_schemas("dissemination")
        api_versions.drop_live_schema("support")
        api_versions.create_live_schemas("support")
