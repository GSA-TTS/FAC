from django.core.management.base import BaseCommand
from audit.cog_over_for_2022 import cog_over_for_2022


class Command(BaseCommand):
    help = """
    Calculate cog / over for 2022 public data and verify.
    """

    def handle(self, *args, **kwargs):
        count, is_match = cog_over_for_2022()
        print(f"Calculated cog / over for {count} rows")
        print(f"Did calculation match with existing 2022 table? --> {is_match}")
