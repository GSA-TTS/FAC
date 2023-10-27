from datetime import datetime
import jwt
import os
import requests

from model_bakery import baker

from django.test import Client, TestCase
from django.urls import reverse

from config import settings
from dissemination.templatetags.field_name_to_label import field_name_to_label
from dissemination.models import (
    General,
    FederalAward,
    Passthrough,
    Finding,
    FindingText,
    CapText,
    Note,
)


class APIViewTests(TestCase):
    def setUp(self):
        self.api_url = settings.POSTGREST.get("URL")

    def create_payload(self, role="api_fac_gov"):
        payload = {
            # PostgREST only cares about the role.
            "role": role,
            "created": datetime.today().isoformat(),
        }
        return payload

    def test_postgrest_url_is_reachable(self):
        # We must pass a properly signed JWT to access the API
        encoded_jwt = jwt.encode(
            self.create_payload(), os.getenv("PGRST_JWT_SECRET"), algorithm="HS256"
        )
        response = requests.get(
            self.api_url, headers={"Authorization": f"Bearer {encoded_jwt}"}, timeout=10
        )
        self.assertEquals(response.status_code, 200)

    def test_api_fails_without_jwt(self):
        # We must pass a properly signed JWT to access the API
        response = requests.get(self.api_url, timeout=10)
        self.assertEquals(response.status_code, 400)

    def test_api_fails_with_bad_jwt(self):
        # We must pass a properly signed JWT to access the API
        encoded_jwt = jwt.encode(
            self.create_payload(),
            "thisisabadsecretitisveryverybadyeppers",
            algorithm="HS256",
        )
        response = requests.get(
            self.api_url, headers={"Authorization": f"Bearer {encoded_jwt}"}, timeout=10
        )
        self.assertEquals(response.status_code, 401)

    def test_api_fails_with_wrong_role(self):
        # We must pass a properly signed JWT to access the API
        encoded_jwt = jwt.encode(
            self.create_payload(role="thisisnotarole"),
            os.getenv("PGRST_JWT_SECRET"),
            algorithm="HS256",
        )
        response = requests.get(
            self.api_url, headers={"Authorization": f"Bearer {encoded_jwt}"}, timeout=10
        )
        self.assertEquals(response.status_code, 400)


class TemplateTagTests(TestCase):
    def test_field_name_to_label(self):
        """
        Given a field name with underscores like "report_id", it should be converted
        to display like "Report Id"
        """
        sample_field = "report_id"
        converted_sample_field = field_name_to_label(sample_field)
        self.assertEquals(converted_sample_field, "Report Id")

        sample_field = "auditee_contact_title"
        converted_sample_field = field_name_to_label(sample_field)
        self.assertEquals(converted_sample_field, "Auditee Contact Title")


class SummaryViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_public_summary(self):
        """
        A public audit should have a viewable summary, and returns 200.
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=True)
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_private_summary(self):
        """
        A private audit should not have a viewable summary, and returns 404.
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=False)
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_summary_context(self):
        """
        The summary context should include the same data that is in the models.
        Create a bunch of fake DB data under the same report_id. Then, check a few
        fields in the context for the summary page to verify that the fake data persists.
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=True)
        award = baker.make(FederalAward, report_id="2022-12-GSAFAC-0000000001")
        passthrough = baker.make(Passthrough, report_id="2022-12-GSAFAC-0000000001")
        finding = baker.make(Finding, report_id="2022-12-GSAFAC-0000000001")
        finding_text = baker.make(FindingText, report_id="2022-12-GSAFAC-0000000001")
        cap_text = baker.make(CapText, report_id="2022-12-GSAFAC-0000000001")
        note = baker.make(Note, report_id="2022-12-GSAFAC-0000000001")

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEquals(
            response.context["data"]["Awards"][0]["additional_award_identification"],
            award.additional_award_identification,
        )
        self.assertEquals(
            response.context["data"]["Audit Findings"][0]["reference_number"],
            finding.reference_number,
        )
        self.assertEquals(
            response.context["data"]["Audit Findings Text"][0]["finding_ref_number"],
            finding_text.finding_ref_number,
        )
        self.assertEquals(
            response.context["data"]["Corrective Action Plan"][0][
                "contains_chart_or_table"
            ],
            cap_text.contains_chart_or_table,
        )
        self.assertEquals(
            response.context["data"]["Notes to SEFA"][0]["accounting_policies"],
            note.accounting_policies,
        )
