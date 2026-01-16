from datetime import date

from django.test import TestCase
from dissemination.models import General
from dissemination.searchlib.search_resub_tags import (
    build_resub_tag_map,
    attach_resubmission_tags,
)
from model_bakery import baker


class ResubmissionTagTests(TestCase):
    def test_tag_most_recent_single_row_version_gt_1(self):
        row = baker.make(
            General,
            report_id="1001",
            auditee_uei="UEI1",
            audit_year="2022",
            resubmission_version=2,
        )
        tag_map = build_resub_tag_map([row])
        self.assertEqual(tag_map["1001"], "Most Recent")

    def test_highest_version_wins_rest_resubmitted(self):
        row_v2 = baker.make(
            General,
            report_id="1002",
            auditee_uei="UEI2",
            audit_year="2022",
            resubmission_version=2,
        )
        row_v3 = baker.make(
            General,
            report_id="1003",
            auditee_uei="UEI2",
            audit_year="2022",
            resubmission_version=3,
        )

        tag_map = build_resub_tag_map([row_v2, row_v3])
        self.assertEqual(tag_map["1003"], "Most Recent")
        self.assertEqual(tag_map["1002"], "Resubmitted")

    def test_version_le_1_should_not_tag(self):
        row_v1 = baker.make(
            General,
            report_id="1004",
            auditee_uei="UEI3",
            audit_year="2022",
            resubmission_version=1,
        )
        row_v0 = baker.make(
            General,
            report_id="1005",
            auditee_uei="UEI3",
            audit_year="2023",
            resubmission_version=0,  # use 0 instead of None (field is NOT NULL)
        )

        tag_map = build_resub_tag_map([row_v1, row_v0])
        self.assertIsNone(tag_map["1004"])
        self.assertIsNone(tag_map["1005"])

    def test_tie_breaker_fac_accepted_date_then_report_id(self):
        # same version -> later fac_accepted_date should win
        row_earlier = baker.make(
            General,
            report_id="2001",
            auditee_uei="UEI4",
            audit_year="2022",
            resubmission_version=2,
            fac_accepted_date=date(2025, 1, 1),
        )
        row_later = baker.make(
            General,
            report_id="2002",
            auditee_uei="UEI4",
            audit_year="2022",
            resubmission_version=2,
            fac_accepted_date=date(2025, 2, 1),
        )

        tag_map = build_resub_tag_map([row_earlier, row_later])
        self.assertEqual(tag_map["2002"], "Most Recent")
        self.assertEqual(tag_map["2001"], "Resubmitted")

    def test_attach_resubmission_tags(self):
        row1 = baker.make(
            General,
            report_id="3001",
            auditee_uei="UEI5",
            audit_year="2022",
            resubmission_version=2,
        )
        row2 = baker.make(
            General,
            report_id="3002",
            auditee_uei="UEI5",
            audit_year="2022",
            resubmission_version=1,  # no tag
        )
        rows = [row1, row2]

        tag_map = build_resub_tag_map(rows)
        attach_resubmission_tags(rows, tag_map)

        self.assertEqual(row1.resubmission_tag, "Most Recent")
        self.assertIsNone(row2.resubmission_tag)
