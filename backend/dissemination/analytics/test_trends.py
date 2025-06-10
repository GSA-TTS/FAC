from django.test import TestCase

from dissemination.models import (
    Finding,
    General,
    FederalAward,
)
from dissemination.analytics.trends import DisseminationTrendAnalytics

from model_bakery import baker


class TrendAnalyticsTests(TestCase):
    def test_total_submissions_no_year(self):
        """
        Supplying no years should yield [] for total_submissions()
        """
        analytics = DisseminationTrendAnalytics([])
        result = analytics.total_submissions()

        self.assertEqual(result, [])

    def test_total_submissions_none(self):
        """
        Having no submissions should not error for total_submissions()
        """
        analytics = DisseminationTrendAnalytics(["2024"])
        result = analytics.total_submissions()
        expected = [{"total": 0, "year": "2024"}]

        self.assertEqual(result, expected)

    def test_total_submissions(self):
        """
        Only submissions that match provided year(s) should be counted for total_submissions()
        """
        # Correct year
        baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )
        baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )

        # Incorrect year
        baker.make(
            General,
            fac_accepted_date="1776-01-01",
            is_public=True,
        )

        analytics = DisseminationTrendAnalytics(["2024"])
        result = analytics.total_submissions()
        expected = [{"total": 2, "year": "2024"}]

        self.assertEqual(result, expected)

    def test_total_submissions_multi_year(self):
        """
        Should correctly handle multi-year queries for total_submissions()
        """
        # 2024
        baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )
        baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )

        # 1776
        baker.make(
            General,
            fac_accepted_date="1776-01-01",
            is_public=True,
        )

        analytics = DisseminationTrendAnalytics(["1776", "2024"])
        result = analytics.total_submissions()
        expected = [
            {"total": 1, "year": "1776"},
            {"total": 2, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_total_award_volume(self):
        """
        Standard case for total_award_volume() should pass
        """
        baker.make(
            General,
            fac_accepted_date="2022-01-01",
            is_public=True,
        )

        audit_2023 = baker.make(
            General,
            fac_accepted_date="2023-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit_2023,
            amount_expended=99,
        )

        audit_2024 = baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit_2024,
            amount_expended=100,
        )
        baker.make(
            FederalAward,
            report_id=audit_2024,
            amount_expended=50,
        )

        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.total_award_volume()
        expected = [
            {"total": 0, "year": "2022"},
            {"total": 99, "year": "2023"},
            {"total": 150, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_total_award_volume_none(self):
        """
        Having no submissions should not error for total_award_volume()
        """
        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.total_award_volume()
        expected = [
            {"total": 0, "year": "2022"},
            {"total": 0, "year": "2023"},
            {"total": 0, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_total_findings(self):
        """
        Standard case for total_findings() should pass
        """
        baker.make(
            General,
            fac_accepted_date="2022-01-01",
            is_public=True,
        )

        audit_2023 = baker.make(
            General,
            fac_accepted_date="2023-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit_2023,
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit_2023,
            award_reference="AWARD-0001",
        )

        audit_2024 = baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit_2024,
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit_2024,
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit_2024,
            award_reference="AWARD-0001",
        )
        baker.make(
            FederalAward,
            report_id=audit_2024,
            award_reference="AWARD-0002",
        )
        baker.make(
            Finding,
            report_id=audit_2024,
            award_reference="AWARD-0002",
        )

        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.total_findings()
        expected = [
            {"total": 0, "year": "2022"},
            {"total": 1, "year": "2023"},
            {"total": 3, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_total_findings_none(self):
        """
        Having no submissions should not error for total_findings()
        """
        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.total_findings()
        expected = [
            {"total": 0, "year": "2022"},
            {"total": 0, "year": "2023"},
            {"total": 0, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_submissions_with_findings(self):
        """
        Standard case for submissions_with_findings() should pass
        """
        # No 2022 submissions have findings
        baker.make(
            General,
            fac_accepted_date="2022-01-01",
            is_public=True,
        )

        # All (1) 2023 submissions have findings
        audit_2023 = baker.make(
            General,
            fac_accepted_date="2023-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit_2023,
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit_2023,
            award_reference="AWARD-0001",
        )

        # 1 of 2 2024 submissions have findings
        audit_2024 = baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit_2024,
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit_2024,
            award_reference="AWARD-0001",
        )

        audit_2024_no_finding = baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit_2024_no_finding,
            award_reference="AWARD-0001",
        )

        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.submissions_with_findings()
        expected = [
            {"total": 0.0, "year": "2022"},
            {"total": 100.0, "year": "2023"},
            {"total": 50.0, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_submissions_with_findings_none(self):
        """
        Having no submissions should not error for submissions_with_findings()
        """
        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.submissions_with_findings()
        expected = [
            {"total": 0, "year": "2022"},
            {"total": 0, "year": "2023"},
            {"total": 0, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_auditee_risk_profile(self):
        """
        Standard case for auditee_risk_profile() should pass
        """
        # None low risk
        baker.make(
            General,
            fac_accepted_date="2022-01-01",
            is_public=True,
            is_low_risk_auditee="No",
        )

        # 1 of 2 low risk
        baker.make(
            General,
            fac_accepted_date="2023-01-01",
            is_public=True,
            is_low_risk_auditee="No",
        )
        baker.make(
            General,
            fac_accepted_date="2023-01-01",
            is_public=True,
            is_low_risk_auditee="Yes",
        )

        # All low risk
        baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
            is_low_risk_auditee="Yes",
        )

        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        auditee_risk_profile = analytics.auditee_risk_profile()
        expected = [
            {
                "low_risk": 0,
                "low_risk_percent": 0.0,
                "not_low_risk": 1,
                "not_low_risk_percent": 100.0,
                "year": "2022",
            },
            {
                "low_risk": 1,
                "low_risk_percent": 50.0,
                "not_low_risk": 1,
                "not_low_risk_percent": 50.0,
                "year": "2023",
            },
            {
                "low_risk": 1,
                "low_risk_percent": 100.0,
                "not_low_risk": 0,
                "not_low_risk_percent": 0.0,
                "year": "2024",
            },
        ]

        self.assertEqual(auditee_risk_profile, expected)

    def test_auditee_risk_profile_none(self):
        """
        Having no submissions should not error for auditee_risk_profile()
        """
        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.auditee_risk_profile()
        expected = [
            {
                "low_risk": 0,
                "low_risk_percent": 0,
                "not_low_risk": 0,
                "not_low_risk_percent": 0,
                "year": "2022",
            },
            {
                "low_risk": 0,
                "low_risk_percent": 0,
                "not_low_risk": 0,
                "not_low_risk_percent": 0,
                "year": "2023",
            },
            {
                "low_risk": 0,
                "low_risk_percent": 0,
                "not_low_risk": 0,
                "not_low_risk_percent": 0,
                "year": "2024",
            },
        ]

        self.assertEqual(result, expected)

    def test_risk_profile_vs_findings(self):
        """
        Standard case for risk_profile_vs_findings() should pass
        """
        # 2022 submissions have findings and aren't low risk
        baker.make(
            General,
            fac_accepted_date="2022-01-01",
            is_public=True,
            is_low_risk_auditee="No",
        )

        # All (1) 2023 submissions have findings and aren't low risk
        audit_2023 = baker.make(
            General,
            fac_accepted_date="2023-01-01",
            is_public=True,
            is_low_risk_auditee="No",
        )
        baker.make(
            FederalAward,
            report_id=audit_2023,
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit_2023,
            award_reference="AWARD-0001",
        )

        # 1 of 2 2024 submissions have findings and 1 of 2 are low risk
        audit_2024 = baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
            is_low_risk_auditee="Yes",
        )
        baker.make(
            FederalAward,
            report_id=audit_2024,
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit_2024,
            award_reference="AWARD-0001",
        )

        audit_2024_no_finding = baker.make(
            General,
            fac_accepted_date="2024-01-01",
            is_public=True,
            is_low_risk_auditee="No",
        )
        baker.make(
            FederalAward,
            report_id=audit_2024_no_finding,
            award_reference="AWARD-0001",
        )

        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.risk_profile_vs_findings()
        expected = [
            {"audits_with_findings": 0.0, "not_low_risk": 100.0, "year": "2022"},
            {"audits_with_findings": 100.0, "not_low_risk": 100.0, "year": "2023"},
            {"audits_with_findings": 50.0, "not_low_risk": 50.0, "year": "2024"},
        ]

        self.assertEqual(result, expected)

    def test_risk_profile_vs_findings_none(self):
        """
        Having no submissions should not error for risk_profile_vs_findings()
        """
        analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        result = analytics.risk_profile_vs_findings()
        expected = [
            {"audits_with_findings": 0, "not_low_risk": 0, "year": "2022"},
            {"audits_with_findings": 0, "not_low_risk": 0, "year": "2023"},
            {"audits_with_findings": 0, "not_low_risk": 0, "year": "2024"},
        ]

        self.assertEqual(result, expected)
