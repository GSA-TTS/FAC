from django.test import TestCase

from model_bakery import baker

from .models import ELECAUDITHEADER, ReportMigrationStatus


class CensusHistoricalMigrationTests(TestCase):
    def test_can_load_elecauditheader_model(self):
        gen = ELECAUDITHEADER.objects.all()
        self.assertIsNotNone(gen)
        baker.make(ELECAUDITHEADER).save()
        gen = ELECAUDITHEADER.objects.all()
        self.assertEquals(len(gen), 1)

    def test_can_load_report_migration_status_model(self):
        report_migration_status = ReportMigrationStatus.objects.all()
        self.assertIsNotNone(report_migration_status)
        baker.make(ReportMigrationStatus).save()
        report_migration_status = ReportMigrationStatus.objects.all()
        self.assertEquals(len(report_migration_status), 1)
