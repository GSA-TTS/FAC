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
    if CognizantBaseline.objects.count() == 0:
        print("CognizantBaseline table is empty - Loading data into table.")
        count = load_all_cog_from_csv()
        return count

    print("CognizantBaseline table contains data - Updating table with csv.")
    count = update_cogbaseline_w_csv()
    return count


def creat_df_from_csv():
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
    return df


def update_cogbaseline_w_csv():
    print(
        "At start - row count for CognizantBaseline = ",
        CognizantBaseline.objects.count(),
    )
    CognizantBaseline.objects.filter(source="Census", is_active=True).delete()
    print(
        "After deleting active rows - row count for CognizantBaseline = ",
        CognizantBaseline.objects.count(),
    )
    df = creat_df_from_csv()
    cogbaseline_inactives = CognizantBaseline.objects.filter(
        source="Census", is_active=False
    )
    for cogbaseline_inactive in cogbaseline_inactives:
        df = df[
            ~(
                (df["dbkey"] == cogbaseline_inactive["dbkey"])
                & (df["ein"] == cogbaseline_inactive["ein"])
                & (df["uei"] == cogbaseline_inactive["uei"])
            )
        ]
    save_df_to_cogbaseline(df)
    print(
        "At end - row count for CognizantBaseline = ",
        CognizantBaseline.objects.count(),
    )
    rows_updated_in_cogbaseline = df.shape[0]
    return rows_updated_in_cogbaseline


def save_df_to_cogbaseline(df):
    data = df.to_dict("records")
    for item in data:
        CognizantBaseline(
            dbkey=item["dbkey"],
            ein=item["ein"],
            uei=item["uei"],
            cognizant_agency=item["cognizant_agency"],
            date_assigned=item["date_assigned"],
            is_active=item["is_active"],
            source="Census",
        ).save()


def load_all_cog_from_csv():
    df = creat_df_from_csv()
    save_df_to_cogbaseline(df)
    return CognizantBaseline.objects.count()
