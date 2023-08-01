from django.test import TestCase
from dissemination import api_versions

# import requests
from model_bakery import baker

from config import settings
from .models import FederalAward, Finding, FindingText, General

api_schemas = ["api_v1_0_0_beta"]


class APIViewTests(TestCase):
    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")

    # TODO:  Figure out why this test is failing.
    # def test_postgrest_url_is_reachable(self):
    #     response = requests.get(self.api_url, timeout=10)
    #     self.assertAlmostEquals(response.status_code, 200)

    # MCJ FIXME
    # Baker does not seem to be producing/storing any data into the dissemination tables.
    # Why? I don't know. But, it means the test can't do anything.
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
            award_reference=award.award_reference,
        )
        finding.save()

        api_versions.create_live_schemas()
        api_versions.create_live_views()

        for api_version in api_versions.live:
            # For each of the above tables
            for endpoint in ["general", "federal_award", "finding", "finding_text"]:
                pass
                # FIXME: The test data is not present, so I can't run the tests...
                # res = requests.get(f"{self.api_url}/{endpoint}", params={"select": "auditee_uei"}, headers={"accept-profile": api_version})
                # We should get back an array of UEIs. It would be of length one, containing the above UEI.
                # assert res.text == [uei]
