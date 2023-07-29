from django.test import TestCase
from .models import ELECAUDITHEADER
from dissemination.models import General
from . import db, etl
from model_bakery import baker
from faker import Faker


class TestHistETL(TestCase):
    def setUp(self):
        self.db = db.DB()

    def test_db_connection(self):
        print("db = ", self.db)
        self.assertIsNotNone(self.db)

    def test_etl_gen(self):
        fake = Faker()
        gen = baker.make(
            ELECAUDITHEADER,
            AUDITYEAR="2022",
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
        etl.ETL(audit_year=2022).load_general()
        d_gen = General.objects.first()

        self.assertEqual(gen.UEI, d_gen.auditee_uei)
