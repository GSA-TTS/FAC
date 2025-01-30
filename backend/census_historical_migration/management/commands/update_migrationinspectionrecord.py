from django.core.management.base import BaseCommand
from dissemination.models import MigrationInspectionRecord

import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Replace 'GSA_MIGRATION' with '' in policies_content and rate_content
        in census_data of a note in dissemination_migrationinspectionrecord

        Usage:
        manage.py update_migrationinspectionrecord
            --year <audit year>
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--year", help="Year(2016 through 2022)", type=str, default="2022"
        )

    def is_year_invalid(self, year):
        valid_years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022"]
        return year not in valid_years

    def handle(self, *args, **options):
        if ENVIRONMENT != "LOCAL":
            print(f"Environment is not LOCAL, ENVIRONMENT={ENVIRONMENT}")
            return

        year = options.get("year")
        if self.is_year_invalid(year):
            print(
                f"Invalid year {year}.  Expecting 2016 / 2017 / 2018 / 2019 / 2020 / 2021 / 2022"
            )
            return

        migrationinspectionrecords = MigrationInspectionRecord.objects.filter(
            Q(audit_year=year)
        )
        print(f"Count of {year} submissions: {len(migrationinspectionrecords)}")

        for migrationinspectionrecord in migrationinspectionrecords:
            for note in migrationinspectionrecord.note:
                print(note)
