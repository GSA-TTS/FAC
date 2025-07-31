from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker

from audit.cross_validation import (
    sac_validation_shape,
    submission_progress_check,
)
from audit.cross_validation.naming import SECTION_NAMES, find_section_by_name
from .models import Access, SingleAuditChecklist, SubmissionEvent
from .test_views import _load_json

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

        self.assertTemplateUsed(response, "home.html")
        self.assertTrue(response.context["session_expired"])

    def test_phrase_in_page(self):
        """Check for 'General Information form'."""
        baker.make(Access, user=self.user, sac=self.sac)
        self.client.force_login(user=self.user)
        phrase = "General Information form"
        res = self.client.get(
            reverse(
                "audit:SubmissionProgress", kwargs={"report_id": self.sac.report_id}
            )
        )
        self.assertIn(phrase, res.content.decode("utf-8"))

    def test_resubmission_context(self):
        """Check context when resubmission_meta is set"""
        previous_report_id = "some_fake_id"
        self.sac.resubmission_meta = { "previous_report_id": previous_report_id }
        self.sac.save()
        baker.make(Access, user=self.user, sac=self.sac)
        self.client.force_login(user=self.user)
        res = self.client.get(
            reverse(
                "audit:SubmissionProgress", kwargs={"report_id": self.sac.report_id}
            )
        )
        self.assertEqual(res.context["previous_report_id"], previous_report_id)

    def test_resubmission_context_none(self):
        """Check context when resubmission_meta not set"""
        self.sac.resubmission_meta = None
        self.sac.save()
        baker.make(Access, user=self.user, sac=self.sac)
        self.client.force_login(user=self.user)
        res = self.client.get(
            reverse(
                "audit:SubmissionProgress", kwargs={"report_id": self.sac.report_id}
            )
        )
        self.assertEqual(res.context["previous_report_id"], None)

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
            self.assertEqual(result[key]["display"], "inactive")
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
        for section_name, guide in SECTION_NAMES.items():
            camel_name = guide.camel_case
            addl_sections[section_name] = {camel_name: "whatever"}
            addl_sections["federal_awards"] = {"FederalAwards": {"federal_awards": []}}
        addl_sections["general_information"] = info
        del addl_sections["single_audit_report"]
        user = baker.make(User, email="a@a.com")
        sac = baker.make(SingleAuditChecklist, **addl_sections)

        baker.make(
            SubmissionEvent,
            sac=sac,
            user=user,
            event=SubmissionEvent.EventType.GENERAL_INFORMATION_UPDATED,
        )
        baker.make(
            SubmissionEvent,
            sac=sac,
            user=user,
            event=SubmissionEvent.EventType.AUDIT_INFORMATION_UPDATED,
        )
        baker.make(
            SubmissionEvent,
            sac=sac,
            user=user,
            event=SubmissionEvent.EventType.AUDIT_REPORT_PDF_UPDATED,
        )
        baker.make(
            SubmissionEvent,
            sac=sac,
            user=user,
            event=SubmissionEvent.EventType.FEDERAL_AWARDS_UPDATED,
        )
        baker.make(
            SubmissionEvent,
            sac=sac,
            user=user,
            event=SubmissionEvent.EventType.NOTES_TO_SEFA_UPDATED,
        )

        shaped_sac = sac_validation_shape(sac)
        result = submission_progress_check(shaped_sac, sar=True, crossval=False)

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
        info = _load_json(AUDIT_JSON_FIXTURES / filename)
        sac = baker.make(SingleAuditChecklist, general_information=info)
        shaped_sac = sac_validation_shape(sac)
        result = submission_progress_check(shaped_sac, sar=None, crossval=True)
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
