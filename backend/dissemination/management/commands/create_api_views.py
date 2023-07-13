from django.core.management.base import BaseCommand
from dissemination import api_versions

class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate views for the postgrest API.
    """

    # def add_arguments(self, parser):
    #     parser.add_argument("-f", "--file", type=str, help="file name")
    #     parser.add_argument("-a", "--api_version", type=str, help="API version")

    def handle(self, *args, **kwargs):
        # First, we'll create all the APIs that we want live.
        # This will have the effect of updating any APIs that have changed.
        # So, remember: follow our versioning policies:
        # 
        # https://github.com/GSA-TTS/FAC/discussions/1465  
        api_versions.create_live_apis()
        api_versions.deprecate_apis()