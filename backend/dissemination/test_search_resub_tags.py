from django.test import TestCase
from dissemination.models import General
from dissemination.searchlib.search_resub_tags import (
    build_resub_tag_map,
    attach_resubmission_tags,
)
from model_bakery import baker
from audit.models.constants import RESUBMISSION_STATUS


class ResubmissionTagTests(TestCase):
    def test_tag_most_recent(self):
        row = baker.make(
            General,
            report_id="1001",
            resubmission_status=RESUBMISSION_STATUS.MOST_RECENT,
        )
        tag_map = build_resub_tag_map([row])
        self.assertEqual(tag_map["1001"], "Most Recent")

    def test_tag_deprecated(self):
        row = baker.make(
            General,
            report_id="1002",
            resubmission_status=RESUBMISSION_STATUS.DEPRECATED,
        )
        tag_map = build_resub_tag_map([row])
        self.assertEqual(tag_map["1002"], "Resubmitted")

    def test_missing_status_should_not_tag(self):
        row = baker.make(General, report_id="1004", resubmission_status=None)
        tag_map = build_resub_tag_map([row])
        self.assertNotIn("1004", tag_map)

    def test_unknown_status_should_not_tag(self):
        row = baker.make(General, report_id="1005", resubmission_status="REVISED")
        tag_map = build_resub_tag_map([row])
        self.assertNotIn("1005", tag_map)

    def test_attach_resubmission_tags(self):
        row1 = baker.make(
            General,
            report_id="1006",
            resubmission_status=RESUBMISSION_STATUS.MOST_RECENT,
        )
        row2 = baker.make(
            General,
            report_id="1007",
            resubmission_status=RESUBMISSION_STATUS.DEPRECATED,
        )
        rows = [row1, row2]

        # === ADD THIS DEBUG: right after rows are created, BEFORE building the map ===
        def _id(x):  # robust id getter for dicts or model objs
            return x.get("report_id") if isinstance(x, dict) else x.report_id

        def _status(x):
            return (
                x.get("resubmission_status")
                if isinstance(x, dict)
                else getattr(x, "resubmission_status", None)
            )

        print("DEBUG before build_resub_tag_map:")
        for i, r in enumerate(rows, 1):
            print(f"  row{i}: id={_id(r)} status={_status(r)}")

        tag_map = build_resub_tag_map(rows)

        # === ADD THIS DEBUG: right after rows are created, BEFORE building the map ===
        def _id(x):  # robust id getter for dicts or model objs
            return x.get("report_id") if isinstance(x, dict) else x.report_id

        def _status(x):
            return (
                x.get("resubmission_status")
                if isinstance(x, dict)
                else getattr(x, "resubmission_status", None)
            )

        print("DEBUG before build_resub_tag_map:")
        for i, r in enumerate(rows, 1):
            print(f"  row{i}: id={_id(r)} status={_status(r)}")

        attach_resubmission_tags(rows, tag_map)

        # === ADD THIS DEBUG: right after rows are created, BEFORE building the map ===
        def _id(x):  # robust id getter for dicts or model objs
            return x.get("report_id") if isinstance(x, dict) else x.report_id

        def _status(x):
            return (
                x.get("resubmission_status")
                if isinstance(x, dict)
                else getattr(x, "resubmission_status", None)
            )

        print("DEBUG before build_resub_tag_map:")
        for i, r in enumerate(rows, 1):
            print(f"  row{i}: id={_id(r)} status={_status(r)}")

        self.assertEqual(row1.resubmission_tag, "Most Recent")
        row2.resubmission_status = RESUBMISSION_STATUS.UNKNOWN
