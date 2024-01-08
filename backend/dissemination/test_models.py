from django.test import TestCase

from model_bakery import baker

from .models import MigrationInspectionRecord


class MigrationInspectionRecordTests(TestCase):
    def test_can_load_migration_change_record_model(self):
        migration_change_record = MigrationInspectionRecord.objects.all()
        self.assertIsNotNone(migration_change_record)
        baker.make(MigrationInspectionRecord).save()
        migration_change_record = MigrationInspectionRecord.objects.all()
        self.assertEquals(len(migration_change_record), 1)
