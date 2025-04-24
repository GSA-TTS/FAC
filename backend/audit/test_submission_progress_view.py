from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker

from audit.cross_validation import (
    submission_progress_check,
)
from audit.cross_validation.naming import find_section_by_name
from .cross_validation.audit_validation_shape import audit_validation_shape
from .fixtures.audit_information import fake_audit_information
from .fixtures.excel import FORM_SECTIONS
from .models import Access, Audit, History
from .models.constants import EventType
from .test_views import load_json, load_json_audit_data

import datetime


AUDIT_JSON_FIXTURES = Path(__file__).parent / "fixtures" / "json"
User = get_user_model()


class SubmissionProgressViewTests(TestCase):
    """
    The page shows information about a submission and conditionally displays links/other
    affordances for individual sections.
    """

    def setUp(self):
        self.user = baker.make(User)
        self.audit = baker.make(Audit, version=0)
        self.client = Client()

    def test_login_required(self):
        """When an unauthenticated request is made"""

        response = self.client.post(
            reverse(
                "audit:SubmissionProgress",
                kwargs={"report_id": "12345"},
            )
        )

        self.assertTemplateUsed(response, "home.html")
        self.assertTrue(response.context["session_expired"])

    def test_phrase_in_page(self):
        """Check for 'General Information form'."""
        baker.make(Access, user=self.user, audit=self.audit)
        self.client.force_login(user=self.user)
        phrase = "General Information form"
        res = self.client.get(
            reverse(
                "audit:SubmissionProgress", kwargs={"report_id": self.audit.report_id}
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
        info = load_json(AUDIT_JSON_FIXTURES / filename)
        audit = baker.make(Audit, version=0, audit={"general_information": info})
        shaped_audit = audit_validation_shape(audit)

        result = submission_progress_check(shaped_audit, sar=None, crossval=False)
        self.assertEqual(result["general_information"]["display"], "complete")
        self.assertTrue(result["general_information"]["completed"])
        conditional_keys = (
            "additional_ueis",
            "additional_eins",
            "secondary_auditors",
        )
        for key in conditional_keys:
            self.assertEqual(result[key]["display"], "inactive")
        self.assertFalse(result["complete"])
        baker.make(Access, user=self.user, audit=audit)
        self.client.force_login(user=self.user)
        res = self.client.get(
            reverse("audit:SubmissionProgress", kwargs={"report_id": audit.report_id})
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
        geninfofile = "general-information--test0001test--simple-pass.json"
        awardsfile = "federal-awards--test0001test--simple-pass.json"
        audit_data = {
            "is_public": True,
            "audit_information": fake_audit_information(),
            "general_information": load_json(AUDIT_JSON_FIXTURES / geninfofile),
            "notes_to_sefa": {
                "accounting_policies": "Exhaustive",
                "is_minimis_rate_used": "Y",
                "rate_explained": "At great length",
            },
            **load_json_audit_data(awardsfile, FORM_SECTIONS.FEDERAL_AWARDS),
        }

        user = baker.make(User, email="a@a.com")
        audit = baker.make(Audit, version=0, audit=audit_data)

        baker.make(
            History,
            report_id=audit.report_id,
            updated_by=user,
            event=EventType.GENERAL_INFORMATION_UPDATED,
        )
        baker.make(
            History,
            report_id=audit.report_id,
            updated_by=user,
            event=EventType.AUDIT_INFORMATION_UPDATED,
        )
        baker.make(
            History,
            report_id=audit.report_id,
            updated_by=user,
            event=EventType.AUDIT_REPORT_PDF_UPDATED,
        )
        baker.make(
            History,
            report_id=audit.report_id,
            updated_by=user,
            event=EventType.FEDERAL_AWARDS_UPDATED,
        )
        baker.make(
            History,
            report_id=audit.report_id,
            updated_by=user,
            event=EventType.NOTES_TO_SEFA_UPDATED,
        )

        shaped_audit = audit_validation_shape(audit)
        result = submission_progress_check(shaped_audit, sar=True, crossval=False)

        self.assertEqual(result["general_information"]["display"], "complete")
        self.assertTrue(result["general_information"]["completed"])

        self.assertEqual(result["audit_information"]["completed_by"], "a@a.com")
        self.assertIsInstance(
            result["audit_information"]["completed_date"], datetime.datetime
        )

        self.assertEqual(result["federal_awards"]["completed_by"], "a@a.com")
        self.assertIsInstance(
            result["federal_awards"]["completed_date"], datetime.datetime
        )

        self.assertEqual(result["general_information"]["completed_by"], "a@a.com")
        self.assertIsInstance(
            result["general_information"]["completed_date"], datetime.datetime
        )

        self.assertEqual(result["notes_to_sefa"]["completed_by"], "a@a.com")
        self.assertIsInstance(
            result["notes_to_sefa"]["completed_date"], datetime.datetime
        )

        self.assertEqual(result["single_audit_report"]["completed_by"], "a@a.com")
        self.assertIsInstance(
            result["single_audit_report"]["completed_date"], datetime.datetime
        )

        conditional_keys = (
            "additional_ueis",
            "additional_eins",
            "secondary_auditors",
        )
        for key in conditional_keys:
            self.assertEqual(result[key]["display"], "inactive")
        self.assertTrue(result["complete"])

    def test_submission_progress_check_crossval_incomplete(self):
        """
        Check that we return the appropriate incomplete sections.
        """
        filename = "general-information--test0001test--simple-pass.json"
        info = load_json(AUDIT_JSON_FIXTURES / filename)
        audit = baker.make(Audit, version=0, audit={"general_information": info})
        shaped_audit = audit_validation_shape(audit)
        result = submission_progress_check(shaped_audit, sar=None, crossval=True)
        expected = "The following sections are incomplete: Audit Information, Federal Awards, Notes to SEFA, Single Audit Report."
        self.assertEqual(result[0]["error"], expected)

    def test_find_section_by_name(self):
        """
        This test added for test coverage purposes.

        """

        names = (
            "SECONDARY_AUDITORS",
            "SecondaryAuditors",
            "Secondary Auditors",
            "Secondary Auditors",
            "report_submission:secondary-auditors",
            "secondary_auditors",
            "secondary-auditors",
        )

        for name in names:
            self.assertEqual(
                find_section_by_name(name).snake_case, "secondary_auditors"
            )
