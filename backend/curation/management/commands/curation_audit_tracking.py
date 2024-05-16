from django.core.management.base import BaseCommand
# These are pulled from a library so they can be used 
# elsewhere in the code. 
from curation.curationlib.curation_audit_tracking import (
    init_audit_curation,
    enable_audit_curation,
    disable_audit_curation
)
class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate access tables for the postgrest API.
    """

    def add_arguments(self, parser):
        parser.add_argument("-i", "--init", action="store_true", default=False)
        parser.add_argument("-e", "--enable", action="store_true", default=False)
        parser.add_argument("-d", "--disable", action="store_true", default=False)

    def handle(self, *args, **options):
        if options["init"]:
            init_audit_curation()
        elif options["enable"]:
            enable_audit_curation()
        elif options["disable"]:
            disable_audit_curation()
