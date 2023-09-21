import pandas as pd
from os import path

from django.core.management.base import BaseCommand
from support.models import CognizantBaseline
from config.settings import BASE_DIR
from collections import defaultdict

class Command(BaseCommand):
    help = """
    Populates CognizantBaseline using Cognizant_Agencies_2021_2025.csv
    obtained from https://facdissem.census.gov/PublicDataDownloads.aspx.
    """

    def handle(self, *args, **kwargs):
        count = load_cog_2021_2025()
        print(f"Loaded {count} rows to baseline table")


def load_cog_2021_2025():
    dtypes = defaultdict(lambda: str)
    file_path = path.join(BASE_DIR, "support/fixtures/", "census_baseline.csv")
    df = pd.read_csv(file_path, dtype=dtypes)
    df = df.drop(columns=["AUDITEENAME"])
    df = df.rename(
        columns={
            "DBKEY": "dbkey",
            "EIN": "ein",
            "UEI": "uei",
            "COGAGENCY": "cognizant_agency",
            "DATE_ADDED": "date_assigned",
        }
    )
    df["date_assigned"] = pd.to_datetime(df["date_assigned"], utc=True)
    df["is_active"] = True
    CognizantBaseline.objects.all().delete()
    data = df.to_dict("records")

    for item in data:
        CognizantBaseline(
            dbkey=item["dbkey"],
            ein=item["ein"],
            uei=item["uei"],
            cognizant_agency=item["cognizant_agency"],
            date_assigned=item["date_assigned"],
            is_active=item["is_active"],
        ).save()
    return CognizantBaseline.objects.count()
