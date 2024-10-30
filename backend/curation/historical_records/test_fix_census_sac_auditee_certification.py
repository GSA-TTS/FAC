import unittest
from unittest.mock import MagicMock, patch

from audit.models import SingleAuditChecklist
from census_historical_migration.models import ELECAUDITHEADER
from .fix_census_sac_auditee_certification import update_census_sac_auditee_name
from model_bakery import baker


class TestUpdateCensusSacAuditeeName(unittest.TestCase):

    @patch.object(SingleAuditChecklist, "save", MagicMock())
    def test_update_census_sac_auditee_name_with_valid_audit_header(self):
        sac = baker.make(
            SingleAuditChecklist,
            auditee_certification={
                "auditee_signature": {
                    "auditee_name": "Old Name",
                    "auditee_title": "Old Title",
                }
            },
        )
        audit_header = baker.make(
            ELECAUDITHEADER,
            AUDITEECERTIFYNAME="Auditee Name",
            AUDITEECERTIFYTITLE="Auditee Title",
        )

        update_census_sac_auditee_name(sac, audit_header)

        self.assertEqual(
            sac.auditee_certification["auditee_signature"]["auditee_name"],
            "Auditee Name",
        )
        self.assertEqual(
            sac.auditee_certification["auditee_signature"]["auditee_title"],
            "Auditee Title",
        )

    @patch.object(SingleAuditChecklist, "save", MagicMock())
    def test_update_census_sac_auditee_name_with_gsa_migration(self):
        # Arrange
        sac = baker.make(
            SingleAuditChecklist,
            auditee_certification={
                "auditee_signature": {
                    "auditee_name": "Old Name",
                    "auditee_title": "Old Title",
                }
            },
        )
        audit_header = baker.make(
            ELECAUDITHEADER,
            AUDITEECERTIFYNAME="",
            AUDITEECERTIFYTITLE="Auditee Title",
        )  # Empty AUDITEECERTIFYNAME is replaced with GSA_MIGRATION

        update_census_sac_auditee_name(sac, audit_header)

        self.assertEqual(
            sac.auditee_certification["auditee_signature"]["auditee_name"],
            "GSA_MIGRATION",
        )
        self.assertEqual(
            sac.auditee_certification["auditee_signature"]["auditee_title"],
            "Auditee Title",
        )

    @patch.object(SingleAuditChecklist, "save", MagicMock())
    def test_update_census_sac_auditee_name_preserves_existing_data_in_auditee_signature(
        self,
    ):
        # Arrange
        sac = baker.make(
            SingleAuditChecklist,
            auditee_certification={
                "auditee_signature": {"some_other_field": "existing_value"}
            },
        )
        audit_header = baker.make(
            ELECAUDITHEADER,
            AUDITEECERTIFYNAME="New Name",
            AUDITEECERTIFYTITLE="New Title",
        )

        update_census_sac_auditee_name(sac, audit_header)

        auditee_signature = sac.auditee_certification["auditee_signature"]
        self.assertEqual(auditee_signature["auditee_name"], "New Name")
        self.assertEqual(auditee_signature["auditee_title"], "New Title")
        self.assertEqual(auditee_signature["some_other_field"], "existing_value")
