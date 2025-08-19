from django.test import TestCase
from dissemination.searchlib.search_resub_tags import (
    build_resub_tag_map,
    attach_resubmission_tags,
)


class ResubmissionTagTests(TestCase):
    def test_tag_most_recent(self):
        rows = [
            {
                "report_id": "1001",
                "resubmission_status": "MOST_RECENT",
                "resubmission_version": 3,
            }
        ]
        tag_map = build_resub_tag_map(rows)
        self.assertEqual(tag_map["1001"], "Most Recent")

    def test_tag_deprecated(self):
        rows = [
            {
                "report_id": "1002",
                "resubmission_status": "DEPRECATED",
                "resubmission_version": 2,
            }
        ]
        tag_map = build_resub_tag_map(rows)
        self.assertEqual(tag_map["1002"], "Resubmitted")

    def test_tag_deprecated_alias(self):
        rows = [
            {
                "report_id": "1003",
                "resubmission_status": "DEPRECATED_VIA_RESUBMISSION",
                "resubmission_version": 2,
            }
        ]
        tag_map = build_resub_tag_map(rows)
        self.assertEqual(tag_map["1003"], "Resubmitted")

    def test_original_should_not_tag(self):
        rows = [
            {
                "report_id": "1004",
                "resubmission_status": "ORIGINAL",
                "resubmission_version": 3,
            }
        ]
        tag_map = build_resub_tag_map(rows)
        self.assertNotIn("1004", tag_map)

    def test_missing_status_should_not_tag(self):
        rows = [
            {
                "report_id": "1005",
                "resubmission_status": None,
                "resubmission_version": 3,
            }
        ]
        tag_map = build_resub_tag_map(rows)
        self.assertNotIn("1005", tag_map)

    def test_unknown_status_should_not_tag(self):
        rows = [
            {
                "report_id": "1006",
                "resubmission_status": "REVISED",
                "resubmission_version": 3,
            }
        ]
        tag_map = build_resub_tag_map(rows)
        self.assertNotIn("1006", tag_map)

    def test_attach_resubmission_tags(self):
        rows = [
            {
                "report_id": "1007",
                "resubmission_status": "MOST_RECENT",
                "resubmission_version": 3,
            },
            {
                "report_id": "1008",
                "resubmission_status": "ORIGINAL",
                "resubmission_version": 1,
            },
        ]
        tag_map = build_resub_tag_map(rows)
        attach_resubmission_tags(rows, tag_map)
        self.assertEqual(rows[0]["resubmission_tag"], "Most Recent")
        self.assertIsNone(rows[1].get("resubmission_tag"))

    def test_ignore_row_without_report_id(self):
        rows = [{"resubmission_status": "MOST_RECENT", "resubmission_version": 3}]
        tag_map = build_resub_tag_map(rows)
        self.assertEqual(len(tag_map), 0)
