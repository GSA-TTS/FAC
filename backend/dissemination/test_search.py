from django.test import TestCase

from audit.fixtures.audit_information import fake_audit_information
from audit.fixtures.certification import (
    fake_auditee_certification,
    fake_auditor_certification,
)
from audit.fixtures.excel import FORM_SECTIONS
from audit.models import Audit
from audit.models.constants import STATUS
from model_bakery import baker

import datetime
import random
import unittest

from audit.models.utils import (
    generate_audit_indexes,
    convert_utc_to_american_samoa_zone,
)
from audit.test_views import (
    build_auditee_cert_dict,
    build_auditor_cert_dict,
    load_json,
    load_json_audit_data,
    AUDIT_JSON_FIXTURES,
)
from dissemination.searchlib.audit_search import search


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


def generate_valid_audit_for_search(
    is_public=True,
    overrides=None,
    report_id=None,
    submission_status=STATUS.DISSEMINATED,
):
    geninfofile = "general-information--test0001test--simple-pass.json"
    awardsfile = "federal-awards--test0001test--simple-pass.json"
    audit_data = {
        "is_public": is_public,
        "fac_accepted_date": convert_utc_to_american_samoa_zone(
            datetime.datetime.today()
        ),
        "auditee_certification": build_auditee_cert_dict(*fake_auditee_certification()),
        "auditor_certification": build_auditor_cert_dict(*fake_auditor_certification()),
        "audit_information": fake_audit_information(),
        "general_information": load_json(AUDIT_JSON_FIXTURES / geninfofile),
        "notes_to_sefa": {
            "accounting_policies": "Exhaustive",
            "is_minimis_rate_used": "Y",
            "rate_explained": "At great length",
        },
        **load_json_audit_data(awardsfile, FORM_SECTIONS.FEDERAL_AWARDS),
    }
    if overrides:
        audit_data.update(overrides)

    audit = (
        baker.make(
            Audit,
            audit=audit_data,
            version=0,
            report_id=report_id,
            submission_status=submission_status,
        )
        if report_id
        else baker.make(
            Audit, audit=audit_data, version=0, submission_status=submission_status
        )
    )

    indexes = generate_audit_indexes(audit)
    audit.audit.update(indexes)
    audit.save()
    return audit


class SearchGeneralTests(TestCase):

    def test_empty_query(self):
        """
        Given empty query parameters, search_general should return all records
        """
        public_count = random.randint(50, 100)
        private_count = random.randint(50, 100)

        baker.make(
            Audit,
            audit={"is_public": True},
            version=0,
            submission_status=STATUS.DISSEMINATED,
            _quantity=public_count,
        )
        baker.make(
            Audit,
            audit={"is_public": False},
            version=0,
            submission_status=STATUS.DISSEMINATED,
            _quantity=private_count,
        )

        results = search(None)

        assert_results_contain_private_and_public(self, results)
        self.assertEqual(len(results), public_count + private_count)

    def test_name_matches_auditee_name(self):
        """
        Given an entity name, search_general(General) should return records with a matching auditee_name
        """
        auditee_name = "auditeeeeeeee"
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_name": auditee_name}}
        )

        results = search(
            {"names": [auditee_name]},
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_name_matches_auditor_firm_name(self):
        """
        Given an entity name, search_general should return records with a matching auditor_firm_name
        """
        auditor_firm_name = "auditoooooooor"
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditor_firm_name": auditor_firm_name}}
        )

        results = search(
            {"names": [auditor_firm_name]},
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_name_multiple(self):
        """
        Given multiple name terms, search_general should only return records that contain all of the terms
        """
        names = ["city", "bronze"]
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_name": "city of gold"}}
        )
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_name": "city of silver"}}
        )
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_name": "city of bronze"}}
        )
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_name": "bronze city"}}
        )

        results = search({"names": names})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 2)

    def test_name_matches_inexact(self):
        """
        Given a partial name, search_general should return records whose name fields contain the term, even if not an exact match
        """
        auditee_match = generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_name": "the university of somewhere"}
            }
        )
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditor_firm_name": "not this one"}}
        )

        results = search({"names": ["UNIVERSITY"]})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], auditee_match)

    def test_uei_or_ein_matches_uei(self):
        """
        Given a uei_or_ein, search_general should return records with a matching UEI
        """
        auditee_uei = "ABCDEFGHIJKL"
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_uei": auditee_uei}}
        )

        results = search(
            {"uei_or_eins": [auditee_uei]},
        )

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

    def test_uei_or_ein_matches_ein(self):
        """
        Given a uei_or_ein, search_general should return records with a matching EIN
        """
        auditee_ein = "ABCDEFGHIJKL"
        generate_valid_audit_for_search(
            overrides={"general_information": {"ein": auditee_ein}}
        )

        results = search(
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

        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_uei": uei_or_eins[0]}}
        )
        generate_valid_audit_for_search(
            overrides={"general_information": {"ein": uei_or_eins[1]}}
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_uei": "not-looking-for-this-uei"}
            }
        )
        generate_valid_audit_for_search(
            overrides={"general_information": {"ein": "not-looking-for-this-ein"}}
        )

        results = search({"uei_or_eins": uei_or_eins})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 2)

    def test_additional_ein(self):
        """
        Given an EIN, search_general should return records that match on the auditee_ein and records with an applicable additional_ein.
        """
        ein = "123456789"

        # Two target records, one general with the EIN and one general with an applicable additional EIN
        generate_valid_audit_for_search(overrides={"general_information": {"ein": ein}})
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"ein": "not-looking-for-this-ein"},
                "additional_eins": [ein],
            }
        )

        # Two filler records
        generate_valid_audit_for_search(
            overrides={"general_information": {"ein": "not-looking-for-this-ein"}}
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"ein": "not-looking-for-this-ein"},
                "additional_eins": ["not-looking-for-this-additional-ein"],
            }
        )

        results = search({"uei_or_eins": [ein]})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 2)

    def test_additional_uei(self):
        """
        Given an UEI, search_general should return records that match on the auditee_uei and records with an applicable additional_uei.
        """
        uei = "ABCDEFGH0001"

        # Two target records, one general with the UEI and one general with an applicable additional UEI
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_uei": uei},
                "additional_ueis": ["not-looking-for-this-uei"],
            }
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_uei": "not-looking-for-this-uei"},
                "additional_ueis": [uei],
            }
        )

        # Two filler records
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_uei": "not-looking-for-this-uei"},
                "additional_ueis": ["not-looking-for-this-additional-uei"],
            }
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_uei": "not-looking-for-this-uei"},
                "additional_ueis": ["not-looking-for-this-additional-uei"],
            }
        )

        results = search({"uei_or_eins": [uei]})

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
            generate_valid_audit_for_search(
                overrides={"fac_accepted_date": d.strftime("%Y-%m-%d")}
            )
            d += datetime.timedelta(days=1)

        # search for records between June 10 and June 15
        search_start_date = datetime.date(2023, 6, 10)
        search_end_date = datetime.date(2023, 6, 15)

        results = search(
            {
                "start_date": search_start_date,
                "end_date": search_end_date,
            },
        )

        assert_all_results_public(self, results)

        # we should get 6 results, one for each day between June 10-15
        self.assertEqual(len(results), 6)

        for r in results:
            fad = datetime.datetime.strptime(r.fac_accepted_date, "%Y-%m-%d").date()
            self.assertGreaterEqual(fad, search_start_date)
            self.assertLessEqual(fad, search_end_date)

    def test_audit_year(self):
        """
        Given a list of audit years, search_general should return only records where
        audit_year is one of the given years.
        """
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_fiscal_period_end": "2020-01-01"}
            }
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_fiscal_period_end": "2021-01-01"}
            }
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {"auditee_fiscal_period_end": "2022-01-01"}
            }
        )

        results = search({"audit_years": [2016]})
        assert_all_results_public(self, results)
        self.assertEqual(len(results), 0)

        results = search({"audit_years": [2020]})
        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)

        results = search({"audit_years": [2020, 2021, 2022]})
        assert_all_results_public(self, results)
        self.assertEqual(len(results), 3)

    def test_auditee_state(self):
        """Given a state, search_general should return only records with a matching auditee_state"""

        al = generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_state": "AL"}}
        )
        generate_valid_audit_for_search(
            overrides={"general_information": {"auditee_state": "AK"}}
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {
                    "auditee_state": "AZ",
                    "auditee_fiscal_period_end": "2020-01-01",
                    "auditee_uei": "not-looking-for-this-uei",
                }
            }
        )

        # there should be on result for AL
        results = search({"auditee_state": "AL"})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], al)

        # there should be no results for WI
        results = search({"auditee_state": "WI"})

        assert_all_results_public(self, results)
        self.assertEqual(len(results), 0)

    def test_fy_end_month(self):
        """Given an end month, search_general should return only records with a matching fy_end_date"""
        date_target = datetime.date(2022, 1, 1)
        date_filler = datetime.date(2022, 12, 31)

        generate_valid_audit_for_search(
            overrides={
                "general_information": {
                    "auditee_fiscal_period_end": date_target.strftime("%Y-%m-%d")
                }
            }
        )
        generate_valid_audit_for_search(
            overrides={
                "general_information": {
                    "auditee_fiscal_period_end": date_filler.strftime("%Y-%m-%d")
                }
            }
        )

        results = search({"fy_end_month": date_target.month})
        assert_all_results_public(self, results)

        # One result for the target date, with the matching fy_end_date
        self.assertEqual(len(results), 1)
        end_date = datetime.datetime.strptime(
            results[0]
            .audit.get("general_information", {})
            .get("auditee_fiscal_period_end"),
            "%Y-%m-%d",
        ).date()
        self.assertEqual(end_date, date_target)

    def test_entity_type(self):
        """
        Given a list of entity types, search_general should only return records with an entity_type among the list.
        """
        entity_types = [
            "state",
            "local",
            "tribal",
            "higher-ed",
            "non-profit",
            "unknown",
        ]
        for entity_type in entity_types:
            generate_valid_audit_for_search(
                overrides={
                    "general_information": {
                        "user_provided_organization_type": entity_type
                    }
                }
            )

        # Searching for one type yields one result with the correct field
        results = search({"entity_type": [entity_types[0]]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].organization_type, entity_types[0])

        # Searching for several types yields the same number of results
        results = search({"entity_type": entity_types[2:4]})
        self.assertEqual(len(results), 2)

    def test_report_id(self):
        """
        Given a list report IDs, search_general should only return records with a matching report_id.
        """
        report_ids = [
            "2022-04-TSTDAT-0000000001",
            "2022-04-TSTDAT-0000000002",
            "2022-04-TSTDAT-0000000003",
            "2022-04-TSTDAT-0000000004",
            "2022-04-TSTDAT-0000000005",
        ]
        for rid in report_ids:
            generate_valid_audit_for_search(report_id=rid)

        # Searching for one ID yields one result with the correct ID
        results = search({"report_id": [report_ids[0]]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, report_ids[0])

        # Searching for several IDs yields the same number of results
        results = search({"report_id": report_ids[2:4]})
        self.assertEqual(len(results), 2)

    def test_not_disseminated_not_found(self):
        report_id_in_progress = "2022-04-TSTDAT-0000000001"
        report_id_disseminated = "2022-04-TSTDAT-0000000002"

        generate_valid_audit_for_search(
            report_id=report_id_in_progress, submission_status=STATUS.IN_PROGRESS
        )
        generate_valid_audit_for_search(report_id=report_id_disseminated)

        results = search({"report_id": [report_id_in_progress]})
        self.assertEqual(len(results), 0)

        results = search({"report_id": [report_id_disseminated]})
        self.assertEqual(len(results), 1)

        results = search({"report_id": [report_id_in_progress, report_id_disseminated]})
        self.assertEqual(len(results), 1)


class SearchALNTests(TestCase):
    def test_aln_search(self):
        """Given an ALN (or ALNs), search_general should only return records with awards under one of these ALNs."""

        # Extra "stuff" in the awards is needed for cog/over
        prefix_object = generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000001",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "federal_agency_prefix": "12",
                                "three_digit_extension": "345",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            },
        )

        extension_object = generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000002",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "federal_agency_prefix": "98",
                                "three_digit_extension": "765",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            },
        )

        generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000003",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "federal_agency_prefix": "00",
                                "three_digit_extension": "000",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            },
        )

        # Just a prefix
        params_prefix = {"alns": ["12"]}
        results_general_prefix = search(params_prefix)
        self.assertEqual(len(results_general_prefix), 1)

        # Check if the prefix_object's report_id is in the results
        self.assertIn(prefix_object.report_id, results_general_prefix[0].report_id)

        # Prefix + extension
        params_extension = {"alns": ["98.765"]}
        results_general_extension = search(params_extension)

        self.assertEqual(len(results_general_extension), 1)
        self.assertIn(
            extension_object.report_id, results_general_extension[0].report_id
        )

        # Both
        params_both = {"alns": ["12", "98.765"]}
        results_general_both = search(params_both)

        self.assertEqual(len(results_general_both), 2)
        result_report_ids = set(result.report_id for result in results_general_both)
        self.assertSetEqual(
            result_report_ids, {prefix_object.report_id, extension_object.report_id}
        )

    def test_no_associated_awards(self):
        """
        When making an ALN search, there should be no results on a non-existent ALN or on one with no awards under the present conditions.
        """
        # General record with one award.
        generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000001",
            overrides={
                "general_information": {"auditee_fiscal_period_end": "2024-01-01"},
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "award_reference": "2023-0001",
                                "federal_agency_prefix": "00",
                                "three_digit_extension": "000",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                },
            },
        )
        params = {"alns": ["99"], "audit_years": ["2024"]}
        results = search(params)

        self.assertEqual(len(results), 0)

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_finding_my_aln(self):
        """
        When making an ALN search, search_general should return records under that ALN.
        If the record has findings under that ALN, it should have finding_my_aln == True.
        """
        # General record with one award with a finding.
        generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000001",
            overrides={
                "general_information": {"auditee_fiscal_period_end": "2024-01-01"},
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "award_reference": "2023-0001",
                                "federal_agency_prefix": "00",
                                "three_digit_extension": "000",
                                "number_of_audit_findings": 1,
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                },
            },
        )

        params = {"alns": ["00"]}
        results = search(params)

        self.assertEqual(len(results), 1)
        self.assertTrue(
            results[0].finding_my_aln is True and results[0].finding_all_aln is False
        )

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_finding_all_aln(self):
        """
        When making an ALN search, search_general should return records under that ALN.
        If the record has findings NOT under that ALN, it should have finding_all_aln == True.
        """
        # General record with two awards and one finding. Finding 2 is under a different ALN than finding 1.
        generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000002",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "federal_agency_prefix": "11",
                                "three_digit_extension": "111",
                                "number_of_audit_findings": 0,
                                "amount_expended": 500_000,
                            }
                        },
                        {
                            "program": {
                                "award_reference": "2023-0001",
                                "federal_agency_prefix": "99",
                                "three_digit_extension": "999",
                                "number_of_audit_findings": 1,
                                "amount_expended": 500_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        },
                    ],
                }
            },
        )

        params = {"alns": ["11"]}
        results = search(params)

        self.assertEqual(len(results), 1)
        self.assertTrue(
            results[0].finding_my_aln is False and results[0].finding_all_aln is True
        )

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_finding_my_aln_and_finding_all_aln(self):
        """
        When making an ALN search, search_general should return records under that ALN.
        If the record has findings both under that ALN and NOT under that ALN, it should have finding_my_aln == True and finding_all_aln == True.
        """
        # General record with two awards and two findings. Awards are under different ALNs.
        generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000003",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "award_reference": "2023-0001",
                                "federal_agency_prefix": "22",
                                "three_digit_extension": "222",
                                "number_of_audit_findings": 1,
                                "amount_expended": 500_000,
                            }
                        },
                        {
                            "program": {
                                "award_reference": "2023-0002",
                                "federal_agency_prefix": "99",
                                "three_digit_extension": "999",
                                "number_of_audit_findings": 1,
                                "amount_expended": 500_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        },
                    ],
                }
            },
        )

        params = {"alns": ["22"]}
        results = search(params)

        self.assertEqual(len(results), 1)
        self.assertTrue(
            results[0].finding_my_aln is True and results[0].finding_all_aln is True
        )

    @unittest.skip("Skipping while ALN columns are disabled.")
    def test_alns_no_findings(self):
        # General record with one award and no findings.
        generate_valid_audit_for_search(
            report_id="2022-04-TSTDAT-0000000004",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "award_reference": "2023-0001",
                                "federal_agency_prefix": "33",
                                "three_digit_extension": "333",
                                "number_of_audit_findings": 0,
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            },
        )

        params = {"alns": ["33"]}
        results = search(params)

        self.assertEqual(len(results), 1)
        self.assertTrue(
            results[0].finding_my_aln is False and results[0].finding_all_aln is False
        )


class SearchAdvancedFilterTests(TestCase):
    def test_search_federal_program_name(self):
        """
        When making a search on federal program name, search_federal_program_name
        should only return records with an award of that type.
        """
        generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Foo",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            }
        )
        generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Bar",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            }
        )
        generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Yub Nub",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            }
        )

        # Search for multiple program valid names
        params = {"federal_program_name": ["Foo", "Bar"]}
        results = search(params)
        self.assertEqual(len(results), 2)
        name_results = []
        for result in results:
            name_results.extend(result.program_names)
        # TODO: Something is adding quotes, we should confirm this isn't an issue elsewhere.
        name_results = [name.replace('"', "") for name in name_results]
        self.assertIn("Foo", name_results)
        self.assertIn("Bar", name_results)

        # Search for a single valid program name
        params = {"federal_program_name": ["Foo"]}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].program_names[0].replace('"', ""), "Foo")

        # Search for an invalid program name
        params = {"federal_program_name": ["Baz"]}
        results = search(params)
        self.assertEqual(len(results), 0)

        # Handle delimiters, ignore case
        params = {"federal_program_name": ["nub,yub"]}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].program_names[0].replace('"', ""), "Yub Nub")

    def test_search_cog_or_oversight(self):
        """
        When making a search on major program, search_cog_or_oversight should
        only return records with an award of that type.
        """
        cog = generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Foo",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            }
        )
        cog.audit.update({"cognizant_agency": 42, "oversight_agency": None})
        cog.save()

        oversight = generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Foo",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            }
        )
        oversight.audit.update({"cognizant_agency": None, "oversight_agency": "24"})
        oversight.save()

        # Either cog or over with no agency should return all
        params = {"agency_name": None, "cog_or_oversight": "either"}
        results = search(params)
        self.assertEqual(len(results), 2)

        # Unused agency should return nothing
        params = {"agency_name": 99, "cog_or_oversight": "either"}
        results = search(params)
        self.assertEqual(len(results), 0)

        # Either cog or over with valid agency
        params = {"agency_name": 42, "cog_or_oversight": "either"}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, cog.report_id)

        # Cog with valid agency
        params = {"agency_name": 42, "cog_or_oversight": "cog"}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, cog.report_id)

        # Over with valid agency
        params = {"agency_name": 24, "cog_or_oversight": "oversight"}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, oversight.report_id)

    def test_search_findings(self):
        """
        When making a search on a particular type of finding, search_general should only return records with a finding of that type.
        """
        findings_fields = [
            "modified_opinion",
            "other_findings",
            "material_weakness",
            "significant_deficiency",
            "other_matters",
            "questioned_costs",
        ]

        # For every field, create a General object with an associated Finding with a 'Y' in that field.
        for field in findings_fields:
            audit_data = {
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "award_reference": "2023-001",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                                "number_of_audit_findings": 1,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                },
                "findings_uniform_guidance": [
                    {
                        "program": {"award_reference": "2023-001"},
                        "modified_opinion": "N" if field != "modified_opinion" else "Y",
                        "other_findings": "N" if field != "other_findings" else "Y",
                        "material_weakness": (
                            "N" if field != "material_weakness" else "Y"
                        ),
                        "significant_deficiency": (
                            "N" if field != "significant_deficiency" else "Y"
                        ),
                        "other_matters": "N" if field != "other_matters" else "Y",
                        "questioned_costs": "N" if field != "questioned_costs" else "Y",
                    }
                ],
            }
            generate_valid_audit_for_search(overrides=audit_data)

        # Now generate a repeat_finding:
        generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "award_reference": "2023-001",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                                "number_of_audit_findings": 1,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                },
                "findings_uniform_guidance": [
                    {
                        "program": {"award_reference": "2023-001"},
                        "findings": {"prior_references": "2022-001"},
                        "modified_opinion": "N",
                        "other_findings": "N",
                        "material_weakness": "N",
                        "significant_deficiency": "N",
                        "other_matters": "Y",
                        "questioned_costs": "N",
                    }
                ],
            }
        )

        # One field returns the one appropriate general
        params = {"findings": ["is_modified_opinion"]}
        results = search(params)
        self.assertEqual(len(results), 1)

        # Three fields returns three appropriate generals
        params = {
            "findings": [
                "is_other_findings",
                "is_material_weakness",
                "is_significant_deficiency",
            ],
        }
        results = search(params)
        self.assertEqual(len(results), 3)

        # Garbage fields don't match any, so nothing will come back
        params = {"findings": ["a_garbage_field"]}
        results = search(params)
        self.assertEqual(len(results), 0)

    def test_search_direct_funding(self):
        """
        When making a search on direct/passthrough funding, search_general should only return records with an award of that type.
        """
        direct = generate_valid_audit_for_search(
            report_id="DIRECT",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Foo",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            },
        )

        passthrough = generate_valid_audit_for_search(
            report_id="PASSTHROUGH",
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Foo",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                            },
                            "direct_or_indirect_award": {"is_direct": "N"},
                        }
                    ],
                }
            },
        )

        params = {"direct_funding": ["direct_funding"]}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, direct.report_id)

        params = {"direct_funding": ["passthrough_funding"]}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, passthrough.report_id)

        # One can search on both, even if there's not much reason to.
        params = {
            "direct_funding": ["direct_funding", "passthrough_funding"],
        }
        results = search(params)
        self.assertEqual(len(results), 2)

    def test_search_major_program(self):
        """
        When making a search on major program, search_general should only return records with an award of that type.
        """
        major = generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Foo",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                                "is_major": "Y",
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            }
        )

        non_major = generate_valid_audit_for_search(
            overrides={
                "federal_awards": {
                    "total_amount_expended": 1_000_000,
                    "awards": [
                        {
                            "program": {
                                "program_name": "Foo",
                                "federal_agency_prefix": "93",
                                "amount_expended": 1_000_000,
                                "is_major": "N",
                            },
                            "direct_or_indirect_award": {"is_direct": "Y"},
                        }
                    ],
                }
            }
        )

        params = {"major_program": ["True"]}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, major.report_id)

        params = {"major_program": ["False"]}
        results = search(params)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].report_id, non_major.report_id)

    def test_search_type_requirement(self):
        """
        When making a search on type requirement, search_general should only return records with a matching combination.
        """
        type_requirements = [
            "P",
            "N",
            "L",
            "I",
            "AB",
        ]
        # For each type requirement, generate a general object and a matching award & finding.
        # The award is necessary for the materialized view to pick up the Finding
        for tr in type_requirements:
            generate_valid_audit_for_search(
                overrides={
                    "federal_awards": {
                        "total_amount_expended": 1_000_000,
                        "awards": [
                            {
                                "program": {
                                    "program_name": "Foo",
                                    "federal_agency_prefix": "93",
                                    "amount_expended": 1_000_000,
                                    "is_major": "N",
                                },
                                "direct_or_indirect_award": {"is_direct": "Y"},
                            }
                        ],
                    },
                    "findings_uniform_guidance": [
                        {"program": {"compliance_requirement": tr}}
                    ],
                }
            )

        params = {
            "type_requirement": [type_requirements[0]],
        }
        results = search(params)
        self.assertEqual(len(results), 1)

        params = {
            "type_requirement": type_requirements[2:4],
        }
        results = search(params)
        self.assertEqual(len(results), 2)


class SearchSortTests(TestCase):
    def test_sort_cog_over(self):
        """
        When sorting on COG/OVER, the appropriate records should come back first.
        """
        for agency_number in ["02", "03", "01"]:
            cog = generate_valid_audit_for_search(
                overrides={
                    "federal_awards": {
                        "total_amount_expended": 1_000_000,
                        "awards": [
                            {
                                "program": {
                                    "program_name": "Foo",
                                    "federal_agency_prefix": "93",
                                    "amount_expended": 1_000_000,
                                },
                                "direct_or_indirect_award": {"is_direct": "Y"},
                            }
                        ],
                    }
                }
            )
            cog.audit.update(
                {"cognizant_agency": agency_number, "oversight_agency": None}
            )
            cog.save()

            oversight = generate_valid_audit_for_search(
                overrides={
                    "federal_awards": {
                        "total_amount_expended": 1_000_000,
                        "awards": [
                            {
                                "program": {
                                    "program_name": "Foo",
                                    "federal_agency_prefix": "93",
                                    "amount_expended": 1_000_000,
                                },
                                "direct_or_indirect_award": {"is_direct": "Y"},
                            }
                        ],
                    }
                }
            )
            oversight.audit.update(
                {
                    "cognizant_agency": None,
                    "oversight_agency": agency_number,
                }
            )
            oversight.save()

        ascending = search(
            {
                "order_by": "cog_over",
                "order_direction": "ascending",
            },
        )
        self.assertEqual(len(ascending), 6)
        self.assertEqual(ascending[0].cognizant_agency, None)
        self.assertEqual(ascending[0].oversight_agency, "01")
        self.assertEqual(ascending[len(ascending) - 1].cognizant_agency, "03")
        self.assertEqual(ascending[len(ascending) - 1].oversight_agency, None)

        descending = search(
            {
                "order_by": "cog_over",
                "order_direction": "descending",
            },
        )
        self.assertEqual(len(descending), 6)
        self.assertEqual(descending[0].cognizant_agency, "03")
        self.assertEqual(descending[0].oversight_agency, None)
        self.assertEqual(descending[len(descending) - 1].cognizant_agency, None)
        self.assertEqual(descending[len(descending) - 1].oversight_agency, "01")
