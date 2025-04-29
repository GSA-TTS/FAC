from django.test import TestCase
from model_bakery import baker
from audit.models import Audit

from .errors import err_total_amount_expended
from .check_expenditure_threshold_met import check_expenditure_threshold_met
from .audit_validation_shape import audit_validation_shape

from datetime import date, timedelta


class CheckExpenditureThresholdMetTests(TestCase):
    """
    Tests for check_expenditure_threshold_met
    """

    thresholds = [
        {
            "start": None,  # Beginning of time
            "end": date(2024, 1, 1),
            "minimum": 750000,
        },
        {
            "start": date(2024, 1, 1),
            "end": date(2024, 10, 1),
            "minimum": 900000,
        },
        {
            "start": date(2024, 10, 1),
            "end": None,  # End of time
            "minimum": 1000000,
        },
    ]

    def _make_federal_awards(self, amount_expended_list):
        result = []

        for ae in amount_expended_list:
            result.append(
                {
                    "program": {
                        "amount_expended": ae,
                    }
                }
            )

        return result

    def test_amount_expended_meets_threshold_begin(self):
        """
        A single federal award at a "beginning of time" threshold date should pass.
        """
        auditee_fiscal_period_start = (
            self.thresholds[0]["end"] - timedelta(days=1)
        ).isoformat()
        total = self.thresholds[0]["minimum"]

        audit = baker.make(
            Audit,
            audit={
                "general_information": {
                    "auditee_fiscal_period_start": auditee_fiscal_period_start,
                },
                "federal_awards": {"awards": self._make_federal_awards([total])},
            },
            version=0,
        )

        validation_result = check_expenditure_threshold_met(
            audit_validation_shape(audit),
            thresholds=self.thresholds,
        )

        self.assertEqual(validation_result, [])

    def test_amount_expended_below_threshold_begin(self):
        """
        A single federal award below a "beginning of time" threshold date should fail.
        """
        auditee_fiscal_period_start = (
            self.thresholds[0]["end"] - timedelta(days=1)
        ).isoformat()
        total = self.thresholds[0]["minimum"] - 1

        audit = baker.make(
            Audit,
            audit={
                "general_information": {
                    "auditee_fiscal_period_start": auditee_fiscal_period_start,
                },
                "federal_awards": {"awards": self._make_federal_awards([total])},
            },
            version=0,
        )

        validation_result = check_expenditure_threshold_met(
            audit_validation_shape(audit),
            thresholds=self.thresholds,
        )

        self.assertEqual(
            validation_result, [{"error": err_total_amount_expended(total)}]
        )

    def test_amount_expended_meets_threshold_middle(self):
        """
        A single federal award at a "middle" threshold date should pass.
        """
        auditee_fiscal_period_start = self.thresholds[1]["start"].isoformat()
        total = self.thresholds[1]["minimum"]

        audit = baker.make(
            Audit,
            audit={
                "general_information": {
                    "auditee_fiscal_period_start": auditee_fiscal_period_start,
                },
                "federal_awards": {"awards": self._make_federal_awards([total])},
            },
            version=0,
        )

        validation_result = check_expenditure_threshold_met(
            audit_validation_shape(audit),
            thresholds=self.thresholds,
        )

        self.assertEqual(validation_result, [])

    def test_amount_expended_below_threshold_middle(self):
        """
        A single federal award below a "middle" threshold date should fail.
        """
        auditee_fiscal_period_start = self.thresholds[1]["start"].isoformat()
        total = self.thresholds[1]["minimum"] - 1

        audit = baker.make(
            Audit,
            audit={
                "general_information": {
                    "auditee_fiscal_period_start": auditee_fiscal_period_start,
                },
                "federal_awards": {"awards": self._make_federal_awards([total])},
            },
            version=0,
        )

        validation_result = check_expenditure_threshold_met(
            audit_validation_shape(audit),
            thresholds=self.thresholds,
        )

        self.assertEqual(
            validation_result, [{"error": err_total_amount_expended(total)}]
        )

    def test_amount_expended_meets_threshold_end(self):
        """
        A single federal award at an "end of time" threshold date should pass.
        """
        auditee_fiscal_period_start = (
            self.thresholds[2]["start"] + timedelta(days=1)
        ).isoformat()
        total = self.thresholds[2]["minimum"]

        audit = baker.make(
            Audit,
            audit={
                "general_information": {
                    "auditee_fiscal_period_start": auditee_fiscal_period_start,
                },
                "federal_awards": {"awards": self._make_federal_awards([total])},
            },
            version=0,
        )

        validation_result = check_expenditure_threshold_met(
            audit_validation_shape(audit),
            thresholds=self.thresholds,
        )

        self.assertEqual(validation_result, [])

    def test_amount_expended_below_threshold_end(self):
        """
        A single federal award below an "end of time" threshold date should fail.
        """
        auditee_fiscal_period_start = (
            self.thresholds[2]["start"] + timedelta(days=1)
        ).isoformat()
        total = self.thresholds[2]["minimum"] - 1

        audit = baker.make(
            Audit,
            audit={
                "general_information": {
                    "auditee_fiscal_period_start": auditee_fiscal_period_start,
                },
                "federal_awards": {"awards": self._make_federal_awards([total])},
            },
            version=0,
        )

        validation_result = check_expenditure_threshold_met(
            audit_validation_shape(audit),
            thresholds=self.thresholds,
        )

        self.assertEqual(
            validation_result, [{"error": err_total_amount_expended(total)}]
        )

    def test_absolute_amount_expended_meets_threshold(self):
        """
        Multiple awards whose absolute values meet the threshold should pass.
        """
        auditee_fiscal_period_start = self.thresholds[1]["start"].isoformat()
        amount_expended_list = [
            self.thresholds[1]["minimum"] - 500,
            -500,
        ]

        audit = baker.make(
            Audit,
            audit={
                "general_information": {
                    "auditee_fiscal_period_start": auditee_fiscal_period_start,
                },
                "federal_awards": {
                    "awards": self._make_federal_awards(amount_expended_list)
                },
            },
            version=0,
        )

        validation_result = check_expenditure_threshold_met(
            audit_validation_shape(audit),
            thresholds=self.thresholds,
        )

        self.assertEqual(validation_result, [])
