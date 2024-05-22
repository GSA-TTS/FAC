from unittest.mock import patch, MagicMock
from datetime import datetime

from django.test import SimpleTestCase

from .invalid_record import InvalidRecord
from census_historical_migration.end_to_end_core import track_invalid_audit_records


class TestTrackInvalidRecords(SimpleTestCase):

    @patch("dissemination.models.InvalidAuditRecord")
    @patch("census_historical_migration.end_to_end_core.django_timezone")
    def test_no_changes(self, mock_timezone, mock_invalid_audit_record):
        InvalidRecord.reset()
        result = track_invalid_audit_records(2023, "dbkey1", "report1")
        self.assertIsNone(result)
        mock_invalid_audit_record.objects.filter.return_value.delete.assert_not_called()

    @patch("census_historical_migration.end_to_end_core.InvalidAuditRecord")
    @patch("census_historical_migration.end_to_end_core.django_timezone")
    def test_with_changes(self, mock_timezone, mock_invalid_audit_record):
        mock_timezone.now.return_value = datetime(2024, 5, 20)
        InvalidRecord.reset()
        InvalidRecord.append_invalid_general_records(["General record"])
        InvalidRecord.append_invalid_finding_records(["Finding record"])
        InvalidRecord.append_invalid_note_records(["Note record"])
        InvalidRecord.append_invalid_federal_awards_records(["Federal award record"])
        InvalidRecord.append_invalid_secondary_auditor_records(
            ["Secondary auditor record"]
        )

        mock_invalid_audit_record_instance = MagicMock()
        mock_invalid_audit_record.objects.create.return_value = (
            mock_invalid_audit_record_instance
        )

        track_invalid_audit_records(2023, "dbkey1", "report1")

        mock_invalid_audit_record.objects.filter.return_value.delete.assert_called_once_with()
        mock_invalid_audit_record.objects.create.assert_called_once_with(
            audit_year=2023, dbkey="dbkey1", report_id="report1"
        )

        self.assertEqual(
            mock_invalid_audit_record_instance.general, [["General record"]]
        )
        self.assertEqual(
            mock_invalid_audit_record_instance.finding, [["Finding record"]]
        )
        self.assertEqual(mock_invalid_audit_record_instance.note, [["Note record"]])
        self.assertEqual(
            mock_invalid_audit_record_instance.federal_award, [["Federal award record"]]
        )
        self.assertEqual(
            mock_invalid_audit_record_instance.secondary_auditor,
            [["Secondary auditor record"]],
        )

        mock_invalid_audit_record_instance.save.assert_called_once()
        self.assertEqual(InvalidRecord.fields, InvalidRecord.DEFAULT)

    @patch("census_historical_migration.end_to_end_core.InvalidAuditRecord")
    @patch("census_historical_migration.end_to_end_core.django_timezone")
    def test_partial_changes(self, mock_timezone, mock_invalid_audit_record):
        mock_timezone.now.return_value = datetime(2024, 5, 20)
        InvalidRecord.reset()
        InvalidRecord.append_invalid_note_records(["Note record"])

        mock_invalid_audit_record_instance = MagicMock()
        mock_invalid_audit_record.objects.create.return_value = (
            mock_invalid_audit_record_instance
        )

        track_invalid_audit_records(2023, "dbkey1", "report1")

        mock_invalid_audit_record.objects.filter.return_value.delete.assert_called_once_with()
        mock_invalid_audit_record.objects.create.assert_called_once_with(
            audit_year=2023, dbkey="dbkey1", report_id="report1"
        )

        self.assertEqual(mock_invalid_audit_record_instance.note, [["Note record"]])
        mock_invalid_audit_record_instance.save.assert_called_once()
        self.assertEqual(InvalidRecord.fields, InvalidRecord.DEFAULT)
