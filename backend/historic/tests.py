from django.test import TestCase
from .models import ELECAUDITHEADER
from dissemination.models import General
from . import etl
from model_bakery import baker
from faker import Faker


class TestHistETL(TestCase):
    def test_etl_gen_works_for_one(self):
        audit_header = self._fake_AUDITHEADER()
        etl.ETL(audit_year=2022).load_general()
        d_gen = General.objects.first()
        self.assertEqual(audit_header.UEI, d_gen.auditee_uei)

    def test_etl_gen_works_for_many(self):
        for _ in range(1_000):
            self._fake_AUDITHEADER()
        etl.ETL(audit_year=2022).load_general()
        audit_count = ELECAUDITHEADER.objects.count()
        gen_count = General.objects.count()
        self.assertEqual(audit_count, gen_count)

    def _fake_AUDITHEADER(self):
        fake = Faker()
        gen = baker.make(
            ELECAUDITHEADER,
            AUDITYEAR="2022",
            FYSTARTDATE=fake.date(),
            AGENCYCFDA=fake.company(),
            AUDITEENAME=fake.company(),
            AUDITTYPE="Single",
            PERIODCOVERED="Annual",
            AUDITEEEMAIL=fake.ascii_email(),
            CPAEMAIL=fake.ascii_email(),
            COGAGENCY="93",
            OVERSIGHTAGENCY="",
            STATE=fake.state_abbr(),
            CPASTATE=fake.state_abbr(),
            UEI=fake.ssn(),
            EIN=fake.ssn(),
            AUDITOR_EIN=fake.ssn(),
            CPAZIPCODE=fake.zipcode(),
            ZIPCODE=fake.zipcode(),
            DOLLARTHRESHOLD=1000,
            TOTFEDEXPEND=25000,
        )
        gen.save()
        return gen
