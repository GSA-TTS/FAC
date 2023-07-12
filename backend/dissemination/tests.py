from django.test import TestCase
from django.db import connection

# import requests
from model_bakery import baker

from config import settings
from .models import FederalAward, Finding, FindingText, General


class APIViewTests(TestCase):
    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")

    # TODO: Get this test working!
    # def test_postgrest_url_is_reachable(self):
    #     response = requests.get(self.api_url, timeout=10)
    #     self.assertAlmostEquals(response.status_code, 200)

    def test_views_returns_data(self):
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

        with connection.cursor() as cursor:
            # TODO: Need a better way. Creating the views here as the data is in a temporary test databasse
            for file in [
                "init_api_db.sql",
                "db_views.sql",
            ]:
                filename = f"dissemination/api/{file}"
                sql = open(filename, "r").read()
                cursor.execute(sql)

            cursor.execute("SELECT auditee_uei FROM api.vw_general")
            self.assertEquals(cursor.fetchall()[0][0], uei)
            cursor.execute("SELECT auditee_uei FROM api.vw_federal_award")
            self.assertEquals(cursor.fetchall()[0][0], uei)
            cursor.execute("SELECT auditee_uei FROM api.vw_finding")
            self.assertEquals(cursor.fetchall()[0][0], uei)
            cursor.execute("SELECT auditee_uei FROM api.vw_finding_text")
            self.assertEquals(cursor.fetchall()[0][0], uei)
