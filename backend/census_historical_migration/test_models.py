from django.test import TestCase
from django.conf import settings

from model_bakery import baker

from .models import (
    ELECAUDITHEADER,
    ELECEINS,
    ELECAUDITFINDINGS,
    ELECNOTES,
    ELECFINDINGSTEXT,
    ELECCPAS,
    ELECAUDITS,
    ELECPASSTHROUGH,
    ELECUEIS,
    ELECCAPTEXT,
    ReportMigrationStatus,
    MigrationErrorDetail,
)


class CensusHistoricalMigrationTests(TestCase):
    databases = {k for k in settings.DATABASES.keys()}

    def test_can_load_elecauditheader_model(self):
        gen = ELECAUDITHEADER.objects.all()
        self.assertIsNotNone(gen)
        baker.make(ELECAUDITHEADER).save()
        gen = ELECAUDITHEADER.objects.all()
        self.assertEquals(len(gen), 1)

    def test_can_load_eleceins_model(self):
        elec_eins = ELECEINS.objects.all()
        self.assertIsNotNone(elec_eins)
        baker.make(ELECEINS).save()
        elec_eins = ELECEINS.objects.all()
        self.assertEquals(len(elec_eins), 1)

    def test_can_load_elecauditfindings_model(self):
        elec_audit_findings = ELECAUDITFINDINGS.objects.all()
        self.assertIsNotNone(elec_audit_findings)
        baker.make(ELECAUDITFINDINGS).save()
        elec_audit_findings = ELECAUDITFINDINGS.objects.all()
        self.assertEquals(len(elec_audit_findings), 1)

    def test_can_load_elecnotes_model(self):
        elec_notes = ELECNOTES.objects.all()
        self.assertIsNotNone(elec_notes)
        baker.make(ELECNOTES).save()
        elec_notes = ELECNOTES.objects.all()
        self.assertEquals(len(elec_notes), 1)

    def test_can_load_elecfindingstext_model(self):
        elec_findingstext = ELECFINDINGSTEXT.objects.all()
        self.assertIsNotNone(elec_findingstext)
        baker.make(ELECFINDINGSTEXT).save()
        elec_findingstext = ELECFINDINGSTEXT.objects.all()
        self.assertEquals(len(elec_findingstext), 1)

    def test_can_load_eleccpas_model(self):
        elec_cpas = ELECCPAS.objects.all()
        self.assertIsNotNone(elec_cpas)
        baker.make(ELECCPAS).save()
        elec_cpas = ELECCPAS.objects.all()
        self.assertEquals(len(elec_cpas), 1)

    def test_can_load_elecaudits_model(self):
        elec_audits = ELECAUDITS.objects.all()
        self.assertIsNotNone(elec_audits)
        baker.make(ELECAUDITS).save()
        elec_audits = ELECAUDITS.objects.all()
        self.assertEquals(len(elec_audits), 1)

    def test_can_load_elecpassthrough_model(self):
        elec_passthrough = ELECPASSTHROUGH.objects.all()
        self.assertIsNotNone(elec_passthrough)
        baker.make(ELECPASSTHROUGH).save()
        elec_passthrough = ELECPASSTHROUGH.objects.all()
        self.assertEquals(len(elec_passthrough), 1)

    def test_can_load_elecueis_model(self):
        elec_ueis = ELECUEIS.objects.all()
        self.assertIsNotNone(elec_ueis)
        baker.make(ELECUEIS).save()
        elec_ueis = ELECUEIS.objects.all()
        self.assertEquals(len(elec_ueis), 1)

    def test_can_load_eleccaptext_model(self):
        elec_captext = ELECCAPTEXT.objects.all()
        self.assertIsNotNone(elec_captext)
        baker.make(ELECCAPTEXT).save()
        elec_captext = ELECCAPTEXT.objects.all()
        self.assertEquals(len(elec_captext), 1)

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
