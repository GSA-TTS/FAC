import json
import random
from django.test import TestCase
from audit.models import SingleAuditChecklist
from .errors import err_number_of_findings_inconsistent
from .number_of_findings import number_of_findings
from .sac_validation_shape import sac_validation_shape
from model_bakery import baker
from audit.fixtures.excel import (
    CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES,
    FINDINGS_TEXT_ENTRY_FIXTURES,
    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES,
    SECTION_NAMES,
)


class NumberOfFindingsTests(TestCase):
    findings_text = json.loads(
        FINDINGS_TEXT_ENTRY_FIXTURES.read_text(encoding="utf-8")
    )[0]
    findings_uniform_guidance = json.loads(
        FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES.read_text(encoding="utf-8")
    )[0]
    corrective_action_plan = json.loads(
        CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES.read_text(encoding="utf-8")
    )[0]

    def _make_federal_awards(self, findings_count):
        return {
            "FederalAwards": {
                "federal_awards": [
                    {"program": {"number_of_audit_findings": findings_count}}
                ]
            }
        }

    def _make_findings_uniform_guidance(self, findings_count):
        return {
            "FindingsUniformGuidance": {
                "findings_uniform_guidance_entries": [
                    NumberOfFindingsTests.findings_uniform_guidance
                    for _ in range(findings_count)
                ]
            }
        }

    def _make_findings_text(self, findings_count):
        return {
            "FindingsText": {
                "findings_text_entries": [
                    NumberOfFindingsTests.findings_text for _ in range(findings_count)
                ]
            }
        }

    def _make_corrective_action_plan(self, findings_count):
        return {
            "CorrectiveActionPlan": {
                "corrective_action_plan_entries": [
                    NumberOfFindingsTests.corrective_action_plan
                    for _ in range(findings_count)
                ]
            }
        }

    def _make_sac(self, findings_count) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist)
        sac.federal_awards = self._make_federal_awards(findings_count)
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(
            findings_count
        )
        sac.findings_text = self._make_findings_text(findings_count)
        sac.corrective_action_plan = self._make_corrective_action_plan(findings_count)
        return sac

    def test_findings_match_across_all_workbooks(self):
        """
        Check that no error is returned when the number of findings is consistent across all workbooks.
        """
        findings_count = random.randint(2, 9)  # nosec
        sac = self._make_sac(findings_count)
        shaped_sac = sac_validation_shape(sac)
        errors = number_of_findings(shaped_sac)
        self.assertEqual(errors, [])

    def test_findings_mismatch_between_federal_awards_and_findings_uniform_guidance(
        self,
    ):
        """
        Check that an error is returned when the number of findings is inconsistent between Federal Awards and Federal Awards Audit Findings workbooks.
        """
        findings_count = random.randint(5, 9)  # nosec
        mismatch = random.randint(1, 4)  # nosec
        sac = self._make_sac(findings_count)
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(mismatch)
        shaped_sac = sac_validation_shape(sac)
        errors = number_of_findings(shaped_sac)

        self.assertEqual(len(errors), 1)
        expected_error = err_number_of_findings_inconsistent(
            findings_count, mismatch, SECTION_NAMES.FEDERAL_AWARDS_AUDIT_FINDINGS
        )
        self.assertEqual(errors[0]["error"], expected_error)

    def test_findings_mismatch_between_federal_awards_and_corrective_action_plan(self):
        """
        Check that an error is returned when the number of findings is inconsistent between Federal Awards and Corrective Action Plan workbooks.
        """
        findings_count = random.randint(5, 9)  # nosec
        mismatch = random.randint(1, 4)  # nosec
        sac = self._make_sac(findings_count)
        sac.corrective_action_plan = self._make_corrective_action_plan(mismatch)
        shaped_sac = sac_validation_shape(sac)
        errors = number_of_findings(shaped_sac)

        self.assertEqual(len(errors), 1)
        expected_error = err_number_of_findings_inconsistent(
            findings_count, mismatch, SECTION_NAMES.CORRECTIVE_ACTION_PLAN
        )
        self.assertEqual(errors[0]["error"], expected_error)

    def test_findings_mismatch_between_federal_awards_and_findings_text(self):
        """
        Check that an error is returned when the number of findings is inconsistent between Federal Awards and Audit Findings Text workbooks.
        """
        findings_count = random.randint(5, 9)  # nosec
        mismatch = random.randint(1, 4)  # nosec
        sac = self._make_sac(findings_count)
        sac.findings_text = self._make_findings_text(mismatch)
        shaped_sac = sac_validation_shape(sac)
        errors = number_of_findings(shaped_sac)

        self.assertEqual(len(errors), 1)
        expected_error = err_number_of_findings_inconsistent(
            findings_count, mismatch, SECTION_NAMES.AUDIT_FINDINGS_TEXT
        )
        self.assertEqual(errors[0]["error"], expected_error)

    def test_findings_mismatch_between_federal_awards_and_all_workbooks(self):
        """
        Check that an error is returned when the number of findings is inconsistent between Federal Awards and the other workbooks.
        """
        findings_count = random.randint(5, 9)  # nosec
        mismatch = random.randint(1, 4)  # nosec
        sac = self._make_sac(findings_count)
        sac.findings_text = self._make_findings_text(mismatch)
        sac.corrective_action_plan = self._make_corrective_action_plan(mismatch)
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(mismatch)
        shaped_sac = sac_validation_shape(sac)
        errors = number_of_findings(shaped_sac)

        self.assertEqual(len(errors), 3)

        error_messages = [error["error"] for error in errors]

        # Check for the existence of each error message
        expected_error1 = err_number_of_findings_inconsistent(
            findings_count, mismatch, SECTION_NAMES.AUDIT_FINDINGS_TEXT
        )
        self.assertEqual(error_messages.count(expected_error1), 1)

        expected_error2 = err_number_of_findings_inconsistent(
            findings_count, mismatch, SECTION_NAMES.CORRECTIVE_ACTION_PLAN
        )
        self.assertEqual(error_messages.count(expected_error2), 1)

        expected_error3 = err_number_of_findings_inconsistent(
            findings_count, mismatch, SECTION_NAMES.FEDERAL_AWARDS_AUDIT_FINDINGS
        )
        self.assertEqual(error_messages.count(expected_error3), 1)
