from django.test import TestCase

from model_bakery import baker

from .models import ELECAUDITHEADER, FailedSacs, ChangeRecords


class CensusHistoricalMigrationTests(TestCase):
    def test_can_load_elecauditheader_model(self):
        gen = ELECAUDITHEADER.objects.all()
        self.assertIsNotNone(gen)
        baker.make(ELECAUDITHEADER).save()
        gen = ELECAUDITHEADER.objects.all()
        self.assertEquals(len(gen), 1)

    def test_can_load_failed_sacs_model(self):
        failed_sacs = FailedSacs.objects.all()
        self.assertIsNotNone(failed_sacs)
        baker.make(FailedSacs).save()
        failed_sacs = FailedSacs.objects.all()
        self.assertEquals(len(failed_sacs), 1)

    def test_can_load_change_records_model(self):
        change_records = ChangeRecords.objects.all()
        self.assertIsNotNone(change_records)
        baker.make(ChangeRecords).save()
        change_records = ChangeRecords.objects.all()
        self.assertEquals(len(change_records), 1)
