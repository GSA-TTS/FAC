import logging


from django.core.management.base import BaseCommand

from ...loader import load_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Migrate from Census tables to GSAFAC tables
        Usage:
        manage.py run_migration --year <audit_year>
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", help="4-digit Audit Year")

    def handle(self, *args, **options):
        year = options.get("year")
        if not year:
            print("Please specify an audit year")
            return

        load_data(audit_year=year)
