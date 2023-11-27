from django.test import TestCase
from django.conf import settings

from model_bakery import baker

from .models import ELECAUDITHEADER, ReportMigrationStatus, MigrationErrorDetail


class CensusHistoricalMigrationTests(TestCase):
    databases = {k for k in settings.DATABASES.keys()}

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

    def test_can_load_migration_error_detail_model(self):
        migration_error_detail = MigrationErrorDetail.objects.all()
        self.assertIsNotNone(migration_error_detail)
        baker.make(MigrationErrorDetail).save()
        migration_error_detail = MigrationErrorDetail.objects.all()
        self.assertEquals(len(migration_error_detail), 1)
