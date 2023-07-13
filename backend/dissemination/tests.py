from django.test import TestCase
from django.db import connection

# import requests
from model_bakery import baker

from config import settings
from .models import FederalAward, Finding, FindingText, General

api_schemas = ["api_v1_0_0_beta"]


class APIViewTests(TestCase):
    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")

    def test_postgrest_url_is_reachable(self):
        response = requests.get(self.api_url, timeout=10)
        self.assertAlmostEquals(response.status_code, 200)

    def test_views_returns_data(self):
        pass
        uei = "UCL2KRV93"
        finding_ref_number = "2023-001"

        general = baker.make(General, auditee_uei=uei, is_public=True)
        general.save()
        award = baker.make(FederalAward, report_id=general.report_id)
        award.save()
        finding_text = baker.make(
            FindingText,
            report_id=general.report_id,
            finding_ref_number=finding_ref_number,
        )
        finding_text.save()
        finding = baker.make(
            Finding,
            report_id=general.report_id,
            finding_ref_number=finding_text.finding_ref_number,
            award_seq_number=award.award_seq_number,
        )
        finding.save()

        for api_version in api_schemas:
            with connection.cursor() as cursor:
                # TODO: Need a better way. Creating the views here as the data is in a temporary test databasse
                for file in [
                    "init_api_db.sql",
                    "db_views.sql",
                ]:
                    filename = f"dissemination/api/{api_version}/{file}"
                    sql = open(filename, "r").read()
                    cursor.execute(sql)

                cursor.execute(f"SELECT auditee_uei FROM {api_version}.general")
                self.assertEquals(cursor.fetchall()[0][0], uei)
                cursor.execute(f"SELECT auditee_uei FROM {api_version}.federal_award")
                self.assertEquals(cursor.fetchall()[0][0], uei)
                cursor.execute(f"SELECT auditee_uei FROM {api_version}.finding")
                self.assertEquals(cursor.fetchall()[0][0], uei)
                cursor.execute(f"SELECT auditee_uei FROM {api_version}.finding_text")
                self.assertEquals(cursor.fetchall()[0][0], uei)
