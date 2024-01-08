from django.test import TestCase

from model_bakery import baker

from .models import MigrationInspectionRecord


class MigrationInspectionRecordTests(TestCase):
    def test_can_load_migration_inspection_record_model(self):
        migration_inspection_record = MigrationInspectionRecord.objects.all()
        self.assertIsNotNone(migration_inspection_record)
        baker.make(MigrationInspectionRecord).save()
        migration_inspection_record = MigrationInspectionRecord.objects.all()
        self.assertEquals(len(migration_inspection_record), 1)
