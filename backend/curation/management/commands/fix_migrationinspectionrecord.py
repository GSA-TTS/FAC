from django.core.management.base import BaseCommand
from dissemination.models import MigrationInspectionRecord
from config.settings import ENVIRONMENT, GSA_MIGRATION
from django.db.models import Q

import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Replace 'GSA_MIGRATION' with '' in policies_content and rate_content
        of census_data in a note in dissemination_migrationinspectionrecord

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
        if ENVIRONMENT not in [
            "LOCAL",
            "DEVELOPMENT",
            "PREVIEW",
            "STAGING",
            "PRODUCTION",
        ]:
            print(f"Environment is not as expected, ENVIRONMENT={ENVIRONMENT}")
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

        count = 0
        for migrationinspectionrecord in migrationinspectionrecords:
            notes = []
            is_updated = False
            for note in migrationinspectionrecord.note:
                if (
                    note[0]["transformation_functions"][0]
                    == "xform_missing_notes_records"
                ) & (note[0]["census_data"][0]["value"] == GSA_MIGRATION):
                    note[0]["census_data"][0]["value"] = ""
                    is_updated = True
                notes += [note]
            if is_updated:
                migrationinspectionrecord.note = notes
                migrationinspectionrecord.save()
                count += 1

        print("Number of records updated = ", count)
