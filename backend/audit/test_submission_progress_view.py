from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker

from .cross_validation import (
    sac_validation_shape,
    snake_to_camel,
    submission_progress_check,
)
from .models import Access, SingleAuditChecklist
from .test_views import _load_json


AUDIT_JSON_FIXTURES = Path(__file__).parent / "fixtures" / "json"
User = get_user_model()


class SubmissionProgressViewTests(TestCase):
    """
    The page shows information about a submission and conditionally displays links/other
    affordances for individual sections.
    """

    def setUp(self):
        self.user = baker.make(User)
        self.sac = baker.make(SingleAuditChecklist)
        self.client = Client()

    def test_login_required(self):
        """When an unauthenticated request is made"""

        response = self.client.post(
            reverse(
                "audit:SubmissionProgress",
                kwargs={"report_id": "12345"},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_phrase_in_page(self):
        """Check for 'General information form'."""
        baker.make(Access, user=self.user, sac=self.sac)
        self.client.force_login(user=self.user)
        phrase = "General information form"
        res = self.client.get(
            reverse(
                "audit:SubmissionProgress", kwargs={"report_id": self.sac.report_id}
            )
        )
        self.assertIn(phrase, res.content.decode("utf-8"))

    def test_submission_progress_check_geninfo_only(self):
        """
        Check the function containing the logic around which sections are required.

        If the conditional questions all have negative answers and data is absent for
        the rest, return the appropriate shape.
        """
        filename = "general-information--test0001test--simple-pass.json"
        info = _load_json(AUDIT_JSON_FIXTURES / filename)
        sac = baker.make(SingleAuditChecklist, general_information=info)
        shaped_sac = sac_validation_shape(sac)
        result = submission_progress_check(shaped_sac, sar=None, crossval=False)
        self.assertEqual(result["general_information"]["display"], "complete")
        self.assertTrue(result["general_information"]["completed"])
        conditional_keys = (
            "additional_ueis",
            "additional_eins",
            "secondary_auditors",
        )
        for key in conditional_keys:
            self.assertEqual(result[key]["display"], "hidden")
        self.assertFalse(result["complete"])
        baker.make(Access, user=self.user, sac=sac)
        self.client.force_login(user=self.user)
        res = self.client.get(
            reverse("audit:SubmissionProgress", kwargs={"report_id": sac.report_id})
        )
        phrases = (
            "Upload the Additional UEIs workbook",
            "Upload the Additional EINs workbook",
            "Upload the Secondary Auditors workbook",
        )
        for phrase in phrases:
            self.assertNotIn(phrase, res.content.decode("utf-8"))

    def test_submission_progress_check_simple_pass(self):
        """
        Check the function containing the logic around which sections are required.

        If the conditional questions all have negative answers and data is present for
        the rest, return the appropriate shape.


        """
        filename = "general-information--test0001test--simple-pass.json"
        info = _load_json(AUDIT_JSON_FIXTURES / filename)
        addl_sections = {}
        for section_name, camel_name in snake_to_camel.items():
            addl_sections[section_name] = {camel_name: "whatever"}
        addl_sections["general_information"] = info
        sac = baker.make(SingleAuditChecklist, **addl_sections)
        shaped_sac = sac_validation_shape(sac)
        result = submission_progress_check(shaped_sac, sar=None, crossval=False)
        self.assertEqual(result["general_information"]["display"], "complete")
        self.assertTrue(result["general_information"]["completed"])
        conditional_keys = (
            "additional_ueis",
            "additional_eins",
            "secondary_auditors",
        )
        for key in conditional_keys:
            self.assertEqual(result[key]["display"], "hidden")
        self.assertTrue(result["complete"])
