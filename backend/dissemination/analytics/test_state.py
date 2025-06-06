from django.test import TestCase

from dissemination.models import (
    Finding,
    General,
    FederalAward,
)
from dissemination.analytics.state import DisseminationStateAnalytics

from model_bakery import baker


class StateAnalyticsTests(TestCase):
    state = "RI"
    year = "2024"

    def test_single_dissemination_count(self):
        """
        Only submissions that match provided state and year should be counted
        """
        # Correct state and year
        baker.make(
            General,
            auditee_state=self.state,
            fac_accepted_date=f"{self.year}-01-01",
            is_public=True,
        )

        # Correct year but incorrect state
        baker.make(
            General,
            auditee_state="GG",
            fac_accepted_date=f"{self.year}-01-01",
            is_public=True,
        )

        # Correct state but incorrect year
        baker.make(
            General,
            auditee_state=self.state,
            fac_accepted_date=f"1776-01-01",
            is_public=True,
        )

        analytics = DisseminationStateAnalytics(self.year, self.state)
        single_dissemination_count = analytics.single_dissemination_count()

        self.assertEqual(single_dissemination_count, 1)

    def test_single_dissemination_count_none(self):
        """
        Having no submissions should yield 0
        """
        analytics = DisseminationStateAnalytics(self.year, self.state)
        single_dissemination_count = analytics.single_dissemination_count()

        self.assertEqual(single_dissemination_count, 0)

    def test_top_programs(self):
        """
        Standard case for top_programs() should pass
        """
        audit = baker.make(
            General,
            auditee_state=self.state,
            fac_accepted_date=f"{self.year}-01-01",
            is_public=True,
        )

        baker.make(
            FederalAward,
            report_id=audit,
            amount_expended=99,
            federal_program_name="Bar Foo"
        )

        # Same program, so they're summed
        baker.make(
            FederalAward,
            report_id=audit,
            amount_expended=42,
            federal_program_name="Foo Bar"
        )
        baker.make(
            FederalAward,
            report_id=audit,
            amount_expended=42,
            federal_program_name="Foo Bar"
        )

        analytics = DisseminationStateAnalytics(self.year, self.state)
        top_programs = analytics.top_programs()
        expected = [
            {'federal_program_name': 'Bar Foo', 'total_expended': 99},
            {'federal_program_name': 'Foo Bar', 'total_expended': 84},
        ]

        self.assertEqual(top_programs, expected)

    def test_funding_by_entity_type(self):
        """
        Standard case for funding_by_entity_type() should pass
        """
        local_audit = baker.make(
            General,
            auditee_state=self.state,
            fac_accepted_date=f"{self.year}-01-01",
            is_public=True,
            entity_type="local",
        )
        baker.make(
            FederalAward,
            report_id=local_audit,
            amount_expended=42,
        )
        baker.make(
            FederalAward,
            report_id=local_audit,
            amount_expended=42,
        )

        state_audit = baker.make(
            General,
            auditee_state=self.state,
            fac_accepted_date=f"{self.year}-01-01",
            is_public=True,
            entity_type="state",
        )
        baker.make(
            FederalAward,
            report_id=state_audit,
            amount_expended=99,
        )

        analytics = DisseminationStateAnalytics(self.year, self.state)
        funding_by_entity_type = analytics.funding_by_entity_type()
        expected = [
            {'entity_type': 'state', 'total_expended': 99},
            {'entity_type': 'local', 'total_expended': 84},
        ]

        self.assertEqual(funding_by_entity_type, expected)

    def test_programs_with_repeated_findings(self):
        """
        Standard case for programs_with_repeated_findings() should pass
        """
        audit = baker.make(
            General,
            auditee_state=self.state,
            fac_accepted_date=f"{self.year}-01-01",
            is_public=True,
        )
        baker.make(
            FederalAward,
            report_id=audit,
            amount_expended=99,
            federal_program_name="Foo Bar",
            award_reference="AWARD-0001",
        )
        baker.make(
            Finding,
            report_id=audit,
            award_reference="AWARD-0001",
            is_repeat_finding="Y",
        )
        baker.make(
            Finding,
            report_id=audit,
            award_reference="AWARD-0001",
            is_repeat_finding="Y",
        )

        baker.make(
            FederalAward,
            report_id=audit,
            amount_expended=99,
            federal_program_name="Bar Foo",
            award_reference="AWARD-0002",
        )
        baker.make(
            Finding,
            report_id=audit,
            award_reference="AWARD-0002",
            is_repeat_finding="N",
        )
        baker.make(
            Finding,
            report_id=audit,
            award_reference="AWARD-0002",
            is_repeat_finding="Y",
        )

        # This award has no repeated findings, so it shouldn't be counted
        baker.make(
            FederalAward,
            report_id=audit,
            amount_expended=99,
            federal_program_name="Bar Bar",
            award_reference="AWARD-0003",
        )
        baker.make(
            Finding,
            report_id=audit,
            award_reference="AWARD-0003",
            is_repeat_finding="N",
        )

        analytics = DisseminationStateAnalytics(self.year, self.state)
        programs_with_repeated_findings = analytics.programs_with_repeated_findings()
        expected = [
            {'federal_program_name': 'Foo Bar', 'repeat_findings': 2},
            {'federal_program_name': 'Bar Foo', 'repeat_findings': 1},
        ]

        self.assertEqual(programs_with_repeated_findings, expected)
