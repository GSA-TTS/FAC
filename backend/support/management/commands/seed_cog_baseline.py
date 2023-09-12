import pandas as pd
from os import path

from django.core.management.base import BaseCommand
from support.models import CognizantBaseline
from config.settings import BASE_DIR

class Command(BaseCommand):
    help = """
    Populates CognizantBaseline using Cognizant_Agencies_2021_2025.csv 
    obtained from https://facdissem.census.gov/PublicDataDownloads.aspx.
    """

    def handle(self, *args, **kwargs):
        count = load_cog_2021_2025()
        print(f"Loaded {count} rows to baseline table")

def load_cog_2021_2025():
    file_path = path.join(BASE_DIR, 'support/fixtures/', 'census_baseline.csv')
    df = pd.read_csv(file_path)
    df = df.drop(columns=['AUDITEENAME'])
    df = df.rename(columns={'DBKEY':'dbkey', 'EIN':'ein', 'UEI':'uei', 'COGAGENCY':'cognizant_agency', 'DATE_ADDED':'date_assigned'})
    # df['date_assigned'] = df['date_assigned'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d', errors='coerce'))
    df['date_assigned'] = pd.to_datetime(df['date_assigned']).dt.strftime('%Y-%m-%d')
    df['is_active'] = True
    # print(df)
    # print(df.dtypes)
    CognizantBaseline.objects.all().delete()
    data = df.to_dict('records')
    # print(data)

    for item in data:
        print(item)
        CognizantBaseline(
            dbkey=item["dbkey"], 
            ein=item["ein"], 
            uei=item["uei"],
            cognizant_agency=item["cognizant_agency"],
            date_assigned=item["date_assigned"],
            # date_assigned=datetime(df.iloc[0]["date_assigned"], tzinfo=pytz.UTC)
            is_active=item["is_active"]
        ).save()
    return CognizantBaseline.objects.count()