from django.test import TestCase

from model_bakery import baker

from .models import MigrationChangeRecord


class MigrationChangeRecordTests(TestCase):
    def test_can_load_migration_change_record_model(self):
        migration_change_record = MigrationChangeRecord.objects.all()
        self.assertIsNotNone(migration_change_record)
        baker.make(MigrationChangeRecord).save()
        migration_change_record = MigrationChangeRecord.objects.all()
        self.assertEquals(len(migration_change_record), 1)
