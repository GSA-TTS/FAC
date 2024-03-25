import os
from django.db import connection
from django.test import TestCase
from dissemination.models import DisseminationCombined, Finding, General, FederalAward
from dissemination.search import (
    search_general,
    search_alns,
    search,
    is_advanced_search,
)

from model_bakery import baker

import datetime
import random
import unittest


def assert_all_results_public(cls, results):
    for r in results:
        cls.assertTrue(r.is_public)


def assert_results_contain_private_and_public(cls, results):
    """Assert that both public and private results were found."""
    found_public = False
    found_private = False

    for r in results:
        if r.is_public:
            found_public = True
        else:
            found_private = True

        if found_public and found_private:
            break

    cls.assertTrue(found_public, "No public results found.")
    cls.assertTrue(found_private, "No private results found.")


class SearchGeneralTests(TestCase):
    def is_advanced_search(self):
        basic_params = {
            "names": "not_important",
            "uei_or_eins": "not_important",
            "start_date": "not_important",
            "advanced_search_flag": False,
        }
        advanced_params = {
            "names": "not_important",
            "uei_or_eins": "not_important",
            "start_date": "not_important",
            "alns": "not_important",
            "advanced_search_flag": True,
        }

        self.assertTrue(is_advanced_search(advanced_params))
        self.assertFalse(is_advanced_search(basic_params))

    def test_empty_query(self):
        """
        Given empty query parameters, search_general should return all records
        """
        public_count = random.randint(50, 100)
        private_count = random.randint(50, 100)

        baker.make(General, is_public=True, _quantity=public_count)
        baker.make(General, is_public=False, _quantity=private_count)

        results = search_general(General)

        assert_results_contain_private_and_public(self, results)
        self.assertEqual(len(results), public_count + private_count)

    def test_name_matches_auditee_name(self):
        """
        Given an entity name, search_general(General) should return records with a matching auditee_name
        """
        auditee_name = "auditeeeeeeee"
        baker.make(General, is_public=True, auditee_name=auditee_name)

        results = search_general(
            General,
            {"names": [auditee_name]},
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
            General,
            {"names": [auditor_firm_name]},
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_name_multiple(self):
        """
        Given multiple name terms, search_general should only return records that contain all of the terms
        """
        names = ["city", "bronze"]

        baker.make(General, is_public=True, auditee_name="city of gold")
        baker.make(General, is_public=True, auditee_name="city of silver")
        baker.make(General, is_public=True, auditee_name="city of bronze")
        baker.make(General, is_public=True, auditee_name="bronze city")

        results = search_general(General, {"names": names})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 2)

    def test_name_matches_inexact(self):
        """
        Given a partial name, search_general should return records whose name fields contain the term, even if not an exact match
        """
        auditee_match = baker.make(
            General, is_public=True, auditee_name="the university of somewhere"
        )
        baker.make(General, is_public=True, auditor_firm_name="not this one")

        results = search_general(General, {"names": ["UNIVERSITY"]})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], auditee_match)

    def test_uei_or_ein_matches_uei(self):
        """
        Given a uei_or_ein, search_general should return records with a matching UEI
        """
        auditee_uei = "ABCDEFGHIJKL"
        baker.make(General, is_public=True, auditee_uei=auditee_uei)

        results = search_general(
            General,
            {"uei_or_eins": [auditee_uei]},
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
            General,
            {"uei_or_eins": [auditee_ein]},
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

        results = search_general(General, {"uei_or_eins": uei_or_eins})

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
            General,
            {
                "start_date": search_start_date,
                "end_date": search_end_date,
            },
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
            General,
            {
                "cog_or_oversight": "cog",
                "agency_name": "01",
            },
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
            General,
            {
                "cog_or_oversight": "oversight",
                "agency_name": "01",
            },
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].oversight_agency, "01")

    def test_audit_year(self):
        """
        Given a list of audit years, search_general should return only records where
        audit_year is one of the given years.
        """
        baker.make(General, is_public=True, audit_year="2020")
        baker.make(General, is_public=True, audit_year="2021")
        baker.make(General, is_public=True, audit_year="2022")

        results = search_general(
            General,
            {
                "audit_years": [2016],
            },
        )
        assert_all_results_public(self, results)
        self.assertEqual(len(results), 0)

        results = search_general(
            General,
            {
                "audit_years": [2020],
            },
        )
        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

        results = search_general(
            General,
            {
                "audit_years": [2020, 2021, 2022],
            },
        )
        assert_all_results_public(self, results)
        self.assertEqual(len(results), 3)

    def test_auditee_state(self):
        """Given a state, search_general should return only records with a matching auditee_state"""
        al = baker.make(General, is_public=True, auditee_state="AL")
        baker.make(General, is_public=True, auditee_state="AK")
        baker.make(
            General,
            is_public=True,
            auditee_state="AZ",
            audit_year="2020",
            oversight_agency="01",
            auditee_uei="not-looking-for-this-uei",
        )

        # there should be on result for AL
        results = search_general(General, {"auditee_state": "AL"})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], al)

        # there should be no results for WI
        results = search_general(General, {"auditee_state": "WI"})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 0)


class TestMaterializedViewBuilder(TestCase):
    def setUp(self):
        super().setUp()
        self.execute_sql_file("dissemination/sql/create_materialized_views.sql")

    def tearDown(self):
        self.execute_sql_file("dissemination/sql/drop_materialized_views.sql")
        super().tearDown()

    def execute_sql_file(self, relative_path):
        """Execute the SQL commands in the file at the given path."""
        full_path = os.path.join(os.getcwd(), relative_path)
        try:
            with open(full_path, "r") as file:
                sql_commands = file.read()
            with connection.cursor() as cursor:
                cursor.execute(sql_commands)
        except Exception as e:
            print(f"Error executing SQL command: {e}")

    def refresh_materialized_view(self):
        """Refresh the materialized view"""
        self.execute_sql_file("dissemination/sql/refresh_materialized_views.sql")


class SearchALNTests(TestMaterializedViewBuilder):
    def test_aln_search(self):
        """Given an ALN (or ALNs), search_general should only return records with awards under one of these ALNs."""

        prefix_object = baker.make(
            General, is_public=True, report_id="2022-04-TSTDAT-0000000001"
        )
        baker.make(
            FederalAward,
            report_id=prefix_object,
            federal_agency_prefix="12",
            federal_award_extension="345",
        )

        extension_object = baker.make(
            General, is_public=True, report_id="2022-04-TSTDAT-0000000002"
        )
        baker.make(
            FederalAward,
            report_id=extension_object,
            federal_agency_prefix="98",
            federal_award_extension="765",
        )

        gen_object = baker.make(
            General, is_public=True, report_id="2022-04-TSTDAT-0000000003"
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            federal_agency_prefix="00",
            federal_award_extension="000",
        )
        self.refresh_materialized_view()

        # Just a prefix
        params_prefix = {"alns": ["12"]}
        results_general_prefix = search_general(DisseminationCombined, params_prefix)
        results_alns_prefix = search_alns(results_general_prefix, params_prefix)
        self.assertEqual(len(results_alns_prefix), 1)
        # Check if the prefix_object's report_id is in the results
        self.assertIn(prefix_object.report_id, results_alns_prefix[0].report_id)

        # Prefix + extension
        params_extention = {"alns": ["98.765"]}
        results_general_extention = search_general(
            DisseminationCombined, params_extention
        )
        results_alns_extention = search_alns(
            results_general_extention, params_extention
        )
        self.assertEqual(len(results_alns_extention), 1)
        self.assertIn(extension_object.report_id, results_alns_extention[0].report_id)

        # Both
        params_both = {"alns": ["12", "98.765"]}
        results_general_both = search_general(DisseminationCombined, params_both)
        results_alns_both = search_alns(results_general_both, params_both)

        self.assertEqual(len(results_alns_both), 2)
        result_report_ids = set(result.report_id for result in results_alns_both)
        self.assertSetEqual(
            result_report_ids, {prefix_object.report_id, extension_object.report_id}
        )

    def test_no_associated_awards(self):
        """
        When making an ALN search, there should be no results on a non-existent ALN or on one with no awards under the present conditions.
        """
        # General record with one award.
        gen_object = baker.make(
            General,
            report_id="2022-04-TSTDAT-0000000001",
            is_public=True,
            audit_year="2024",
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            award_reference="2023-0001",
            federal_agency_prefix="00",
            federal_award_extension="000",
            findings_count=1,
        )
        self.refresh_materialized_view()
        params = {"alns": ["99"], "audit_years": ["2024"]}
        results_general = search_general(DisseminationCombined, params)
        results_alns = search_alns(results_general, params)

        self.assertEqual(len(results_alns), 0)

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_finding_my_aln(self):
        """
        When making an ALN search, search_general should return records under that ALN.
        If the record has findings under that ALN, it should have finding_my_aln == True.
        """
        # General record with one award with a finding.
        gen_object = baker.make(
            General, is_public=True, report_id="2022-04-TSTDAT-0000000001"
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            award_reference="2023-0001",
            federal_agency_prefix="00",
            federal_award_extension="000",
            findings_count=1,
        )

        params = {"alns": ["00"]}
        results_general = search_general(params)
        results_alns = search_alns(results_general, params)

        self.assertEqual(len(results_alns), 1)
        self.assertTrue(
            results_alns[0].finding_my_aln is True
            and results_alns[0].finding_all_aln is False
        )

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_finding_all_aln(self):
        """
        When making an ALN search, search_general should return records under that ALN.
        If the record has findings NOT under that ALN, it should have finding_all_aln == True.
        """
        # General record with two awards and one finding. Finding 2 is under a different ALN than finding 1.
        gen_object = baker.make(
            General, is_public=True, report_id="2022-04-TSTDAT-0000000002"
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            federal_agency_prefix="11",
            federal_award_extension="111",
            findings_count=0,
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            award_reference="2023-0001",
            federal_agency_prefix="99",
            federal_award_extension="999",
            findings_count=1,
        )

        params = {"alns": ["11"]}
        results_general = search_general(params)
        results_alns = search_alns(results_general, params)

        self.assertEqual(len(results_alns), 1)
        self.assertTrue(
            results_alns[0].finding_my_aln is False
            and results_alns[0].finding_all_aln is True
        )

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_finding_my_aln_and_finding_all_aln(self):
        """
        When making an ALN search, search_general should return records under that ALN.
        If the record has findings both under that ALN and NOT under that ALN, it should have finding_my_aln == True and finding_all_aln == True.
        """
        # General record with two awards and two findings. Awards are under different ALNs.
        gen_object = baker.make(
            General, is_public=True, report_id="2022-04-TSTDAT-0000000003"
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            award_reference="2023-0001",
            federal_agency_prefix="22",
            federal_award_extension="222",
            findings_count=1,
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            award_reference="2023-0002",
            federal_agency_prefix="99",
            federal_award_extension="999",
            findings_count=1,
        )

        params = {"alns": ["22"]}
        results_general = search_general(params)
        results_alns = search_alns(results_general, params)

        self.assertEqual(len(results_alns), 1)
        self.assertTrue(
            results_alns[0].finding_my_aln is True
            and results_alns[0].finding_all_aln is True
        )

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_alns_no_findings(self):
        # General record with one award and no findings.
        gen_object = baker.make(
            General, is_public=True, report_id="2022-04-TSTDAT-0000000004"
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
            findings_count=0,
            federal_agency_prefix="33",
            federal_award_extension="333",
        )

        params = {"alns": ["33"]}
        results_general = search_general(params)
        results_alns = search_alns(results_general, params)

        self.assertEqual(len(results_alns), 1)
        self.assertTrue(
            results_alns[0].finding_my_aln is False
            and results_alns[0].finding_all_aln is False
        )


class SearchAdvancedFilterTests(TestMaterializedViewBuilder):
    def test_search_findings(self):
        """
        When making a search on a particular type of finding, search_general should only return records with a finding of that type.
        """
        findings_fields = [
            {"is_modified_opinion": "Y"},
            {"is_other_findings": "Y"},
            {"is_material_weakness": "Y"},
            {"is_significant_deficiency": "Y"},
            {"is_other_matters": "Y"},
            {"is_questioned_costs": "Y"},
            {"is_repeat_finding": "Y"},
        ]

        # For every field, create a General object with an associated Finding with a 'Y' in that field.
        gen_objects = []
        award_objects = []
        finding_objects = []
        for field in findings_fields:
            general = baker.make(
                General,
                is_public=True,
            )
            award = baker.make(
                FederalAward,
                report_id=general,
                findings_count=1,
                award_reference="2023-001",
            )
            finding = baker.make(
                Finding, report_id=general, award_reference="2023-001", **field
            )
            finding_objects.append(finding)
            gen_objects.append(general)
            award_objects.append(award)
        self.refresh_materialized_view()
        # One field returns the one appropriate general
        params = {"findings": ["is_modified_opinion"], "advanced_search_flag": True}
        results = search(params)
        self.assertEqual(len(results), 1)

        # Three fields returns three appropriate generals
        params = {
            "findings": [
                "is_other_findings",
                "is_material_weakness",
                "is_significant_deficiency",
            ],
            "advanced_search_flag": True,
        }
        results = search(params)
        self.assertEqual(len(results), 3)

        # Garbage fields don't apply any filters, so everything comes back
        params = {"findings": ["a_garbage_field"], "advanced_search_flag": True}
        results = search(params)
        self.assertEqual(len(results), 7)

    def test_search_direct_funding(self):
        """
        When making a search on direct/passthrough funding, search_general should only return records with an award of that type.
        """
        general_direct = baker.make(
            General,
            is_public=True,
        )
        baker.make(FederalAward, report_id=general_direct, is_direct="Y")

        general_passthrough = baker.make(
            General,
            is_public=True,
        )
        baker.make(FederalAward, report_id=general_passthrough, is_direct="N")
        self.refresh_materialized_view()

        params = {"direct_funding": ["direct_funding"], "advanced_search_flag": True}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, general_direct.report_id)

        params = {
            "direct_funding": ["passthrough_funding"],
            "advanced_search_flag": True,
        }
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, general_passthrough.report_id)

        # One can search on both, even if there's not much reason to.
        params = {
            "direct_funding": ["direct_funding", "passthrough_funding"],
            "advanced_search_flag": True,
        }
        results = search(params)
        self.assertEqual(len(results), 2)

    def test_search_major_program(self):
        """
        When making a search on major program, search_general should only return records with an award of that type.
        """
        general_major = baker.make(
            General,
            is_public=True,
        )
        baker.make(FederalAward, report_id=general_major, is_major="Y")

        general_non_major = baker.make(
            General,
            is_public=True,
        )
        baker.make(FederalAward, report_id=general_non_major, is_major="N")
        self.refresh_materialized_view()
        params = {"major_program": ["True"], "advanced_search_flag": True}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, general_major.report_id)

        params = {"major_program": ["False"], "advanced_search_flag": True}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, general_non_major.report_id)
