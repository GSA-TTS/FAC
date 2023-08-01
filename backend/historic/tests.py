from django.test import TestCase
from .models import ELECAUDITHEADER, ELECAUDITS
from dissemination.models import General, FederalAward
from .etl import ETL
from model_bakery import baker
from faker import Faker


class TestHistETL(TestCase):
    def test_etl_gen_works_for_one(self):
        audit_header = self._fake_AUDITHEADER()
        ETL(audit_year=2022).load_general()
        d_gen = General.objects.first()
        self.assertEqual(audit_header.UEI, d_gen.auditee_uei)

    def test_etl_award_works_for_one(self):
        award = self._fake_AUDIT()
        etl = ETL(audit_year=2022)
        etl.load_general()
        etl.load_award()
        d_award = FederalAward.objects.first()
        self.assertEqual(award.FEDERALPROGRAMNAME, d_award.federal_program_name)
        self.assertIsNotNone(d_award.report_id)

    def test_etl_gen_works_for_many(self):
        for _ in range(10):
            self._fake_AUDITHEADER()
        ETL(audit_year=2022).load_general()
        audit_gen_count = ELECAUDITHEADER.objects.count()
        diss_gen_count = General.objects.count()
        self.assertEqual(audit_gen_count, diss_gen_count)

    def test_etl_award_works_for_many(self):
        for _ in range(10):
            self._fake_AUDIT()
        etl = ETL(audit_year=2022)
        etl.load_general()
        etl.load_award()
        audit_award_count = ELECAUDITS.objects.count()
        diss_award_count = FederalAward.objects.count()
        self.assertEqual(audit_award_count, diss_award_count)

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

    def _fake_AUDIT(self):
        gen = self._fake_AUDITHEADER()
        fake = Faker()
        award = []
        for i in range(2):
            award.append(
                baker.make(
                    ELECAUDITS,
                    AUDITYEAR=gen.AUDITYEAR,
                    DBKEY=gen.DBKEY,
                    CFDASEQNUM="0".join(str(i)),
                    EIN=fake.ssn(),
                    CFDA_EXT="001",
                    AMOUNT=200000,
                    LOANBALANCE=40000,
                    PASSTHROUGHAMOUNT=25000,
                    PROGRAMTOTAL=2000000,
                    CLUSTERTOTAL=1000000,
                )
            )
            award[i].save()
        return award[0]
