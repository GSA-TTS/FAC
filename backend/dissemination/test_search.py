from django.test import TestCase

from dissemination.models import General
from dissemination.search import search_general

from model_bakery import baker

import datetime
import random


def assert_all_results_public(cls, results):
    for r in results:
        cls.assertTrue(r.is_public)


class SearchGeneralTests(TestCase):
    def test_empty_query(self):
        """
        Given empty query parameters, search_general should return all public records
        """
        public_count = random.randint(50, 100)
        private_count = random.randint(50, 100)

        baker.make(General, is_public=True, _quantity=public_count)
        baker.make(General, is_public=False, _quantity=private_count)

        results = search_general(
            names=None,
            uei_or_eins=None,
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), public_count)

    def test_name_matches_auditee_name(self):
        """
        Given an entity name, search_general should return records with a matching auditee_name
        """
        auditee_name = "auditeeeeeeee"
        baker.make(General, is_public=True, auditee_name=auditee_name)

        results = search_general(
            names=[auditee_name],
            uei_or_eins=None,
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_name_matches_auditor_firm_name(self):
        """
        Given an entity name, search_general should return records with a matching auditor_firm_name
        """
        auditor_firm_name = "auditoooooooor"
        baker.make(General, is_public=True, auditor_firm_name=auditor_firm_name)

        results = search_general(
            names=[auditor_firm_name],
            uei_or_eins=None,
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_name_multiple(self):
        """
        Given multiple names, search_general should return records that match either name
        """
        names = [
            "auditee-01",
            "auditor-firm-01",
            "this-one-has-no-match",
        ]

        baker.make(General, is_public=True, auditee_name=names[0])
        baker.make(General, is_public=True, auditor_firm_name=names[1])
        baker.make(General, is_public=True, auditee_name="not-looking-for-this-auditee")
        baker.make(
            General, is_public=True, auditor_firm_name="not-looking-for-this-auditor"
        )

        results = search_general(
            names=names,
            uei_or_eins=None,
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 2)

    def test_uei_or_ein_matches_uei(self):
        """
        Given a uei_or_ein, search_general should return records with a matching UEI
        """
        auditee_uei = "ABCDEFGHIJKL"
        baker.make(General, is_public=True, auditee_uei=auditee_uei)

        results = search_general(
            names=None,
            uei_or_eins=[auditee_uei],
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_uei_or_ein_matches_ein(self):
        """
        Given a uei_or_ein, search_general should return records with a matching EIN
        """
        auditee_ein = "ABCDEFGHIJKL"
        baker.make(General, is_public=True, auditee_ein=auditee_ein)

        results = search_general(
            names=None,
            uei_or_eins=[auditee_ein],
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_uei_or_ein_multiple(self):
        """
        Given multiple uei_or_eins, search_general should return records that match either UEI or EIN
        """
        uei_or_eins = [
            "ABCDEFGH0001",
            "ABCDEFGH0002",
            "ABCDEFGH0003",
        ]

        baker.make(General, is_public=True, auditee_uei=uei_or_eins[0])
        baker.make(General, is_public=True, auditee_ein=uei_or_eins[1])
        baker.make(General, is_public=True, auditee_uei="not-looking-for-this-uei")
        baker.make(General, is_public=True, auditee_ein="not-looking-for-this-ein")

        results = search_general(
            names=None,
            uei_or_eins=uei_or_eins,
            start_date=None,
            end_date=None,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 2)

    def test_date_range(self):
        """
        Given a start and end date, search_general should return only records inside the date range
        """

        # seed the database with one record for each day of June
        seed_start_date = datetime.date(2023, 6, 1)
        seed_end_date = datetime.date(2023, 6, 30)

        d = seed_start_date
        while d <= seed_end_date:
            baker.make(General, is_public=True, fac_accepted_date=d)
            d += datetime.timedelta(days=1)

        # search for records between June 10 and June 15
        search_start_date = datetime.date(2023, 6, 10)
        search_end_date = datetime.date(2023, 6, 15)

        results = search_general(
            names=None,
            uei_or_eins=None,
            start_date=search_start_date,
            end_date=search_end_date,
            cog_or_oversight=None,
            agency_name=None,
        )

        assert_all_results_public(self, results)

        # we should get 6 results, one for each day between June 10-15
        self.assertEqual(len(results), 6)

        for r in results:
            self.assertGreaterEqual(r.fac_accepted_date, search_start_date)
            self.assertLessEqual(r.fac_accepted_date, search_end_date)

    def test_cognizant_agency(self):
        """
        Given a cognizant agency name, search_general should return only records with a matching cognizant agency name (not oversight)
        """

        baker.make(General, is_public=True, cognizant_agency="01")
        baker.make(General, is_public=True, cognizant_agency="02")

        baker.make(General, is_public=True, oversight_agency="01")

        results = search_general(
            names=None,
            uei_or_eins=None,
            start_date=None,
            end_date=None,
            cog_or_oversight="Cognizant",
            agency_name="01",
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].cognizant_agency, "01")

    def test_oversight_agency(self):
        """
        Given an oversight agency name, search_general should return only records with a matching oversight agency name (not cognizant)
        """

        baker.make(General, is_public=True, cognizant_agency="01")

        baker.make(General, is_public=True, oversight_agency="01")
        baker.make(General, is_public=True, oversight_agency="02")

        results = search_general(
            names=None,
            uei_or_eins=None,
            start_date=None,
            end_date=None,
            cog_or_oversight="Cognizant",
            agency_name="01",
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].cognizant_agency, "01")
