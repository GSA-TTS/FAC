from django.test import TestCase
from model_bakery import baker

from dissemination.models import General
from dissemination.searchlib.search_resub_tags import (
    add_resub_tag_data,
)
from audit.models.constants import RESUBMISSION_STATUS, RESUBMISSION_TAGS


class ResubmissionTagTests(TestCase):
    def test_v0_no_tag(self):
        """ v0 audits don't get a tag """
        rows = [
            baker.make(
                General,
                report_id="1001",
                auditee_uei="UEI1",
                audit_year="2022",
                resubmission_status=RESUBMISSION_STATUS.MOST_RECENT,
                resubmission_version=0,
            )
        ]
        add_resub_tag_data(rows)
        
        self.assertEqual(rows[0].resubmission_tag, None)

    def test_v1_no_tag(self):
        """ v1 most_recent audits don't get a tag """

        rows = [
            baker.make(
                General,
                report_id="1001",
                auditee_uei="UEI1",
                audit_year="2022",
                resubmission_status=RESUBMISSION_STATUS.MOST_RECENT,
                resubmission_version=1,
            )
        ]
        add_resub_tag_data(rows)

        self.assertEqual(rows[0].resubmission_tag, None)

    def test_v2_most_recent(self):
        """ v2 most_recent audits do get a tag """

        rows = [
            baker.make(
                General,
                report_id="1001",
                auditee_uei="UEI1",
                audit_year="2022",
                resubmission_status=RESUBMISSION_STATUS.MOST_RECENT,
                resubmission_version=2,
            )
        ]
        add_resub_tag_data(rows)

        self.assertEqual(rows[0].resubmission_tag, f"V2 ({RESUBMISSION_TAGS.MOST_RECENT})")

    def test_v1_resub(self):
        """ v1 deprecated audits do get a tag """

        rows = [
            baker.make(
                General,
                report_id="1001",
                auditee_uei="UEI1",
                audit_year="2022",
                resubmission_status=RESUBMISSION_STATUS.DEPRECATED,
                resubmission_version=1,
            )
        ]
        add_resub_tag_data(rows)

        self.assertEqual(rows[0].resubmission_tag, f"V1 ({RESUBMISSION_TAGS.DEPRECATED})")

    def test_mixed(self):
        """ Simple case of audits that get different tags """

        rows = [
            baker.make(
                General,
                report_id="1000",
                auditee_uei="UEI1",
                audit_year="2022",
                resubmission_status=RESUBMISSION_STATUS.MOST_RECENT,
                resubmission_version=1,
            ),
            baker.make(
                General,
                report_id="1001",
                auditee_uei="UEI1",
                audit_year="2022",
                resubmission_status=RESUBMISSION_STATUS.DEPRECATED,
                resubmission_version=1,
            ),
            baker.make(
                General,
                report_id="1002",
                auditee_uei="UEI1",
                audit_year="2022",
                resubmission_status=RESUBMISSION_STATUS.MOST_RECENT,
                resubmission_version=2,
            )
        ]
        add_resub_tag_data(rows)

        self.assertEqual(rows[0].resubmission_tag, None)
        self.assertEqual(rows[1].resubmission_tag, f"V1 ({RESUBMISSION_TAGS.DEPRECATED})")
        self.assertEqual(rows[2].resubmission_tag, f"V2 ({RESUBMISSION_TAGS.MOST_RECENT})")
