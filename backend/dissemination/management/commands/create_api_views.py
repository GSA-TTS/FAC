from django.core.management.base import BaseCommand
from dissemination import api_versions


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate views for the postgrest API.
    """

    def handle(self, *args, **kwargs):
        api_versions.create_live_views()
