from django.test import TestCase
from audit.compare_two_submissions import (
    compare_report_ids,
    in_first_not_second,
    in_second_not_first,
    in_both,
    analyze_pair,
    getattr_default,
    deep_getattr,
    compare_lists_of_objects,
    are_two_sacs_identical,
)
from audit.models import SingleAuditChecklist
from model_bakery import baker
from copy import deepcopy


def setup_mock_db():
    # so I can copy-paste data out of a test DB
    true = True
    false = False

    report_ids = [
        "2025-01-FAKEDB-0000000001",
        "2025-01-FAKEDB-0000000002",
        "2025-01-FAKEDB-0000000003",
    ]
    rids = {}
    for ndx, rid in enumerate(report_ids):
        baker.make(SingleAuditChecklist, report_id=rid)
        rids[f"rid_{ndx+1}"] = rid

    sac_r1 = SingleAuditChecklist.objects.get(report_id=rids["rid_1"])
    sac_r2 = SingleAuditChecklist.objects.get(report_id=rids["rid_2"])

    sac_r1.general_information = {
        "ein": "370906335",
        "audit_type": "single-audit",
        "auditee_uei": "G9LDNMFWZHY7",
        "auditee_zip": "62930",
        "auditor_ein": "430352985",
        "auditor_zip": "62711",
        "auditee_city": "Eldorado",
        "auditee_name": "Eldorado Community Unit School District No. 4",
        "auditor_city": "Springfield",
        "is_usa_based": True,
        "auditee_email": "rhobbs@eld4.org",
        "auditee_phone": "6182739312",
        "auditee_state": "IL",
        "auditor_email": "amandaw@kebcpa.com",
        "auditor_phone": "2177890960",
        "auditor_state": "IL",
        "auditor_country": "USA",
        "auditor_firm_name": "Kerber, Eck & Braeckel LLP",
        "audit_period_covered": "annual",
        "auditee_contact_name": "Ryan Hobbs",
        "auditor_contact_name": "Amanda Wells",
        "auditee_contact_title": "Superintendent",
        "auditor_contact_title": "Senior Manager",
        "multiple_eins_covered": False,
        "multiple_ueis_covered": False,
        "auditee_address_line_1": "2200 Illinois Avenue",
        "auditor_address_line_1": "3200 Robbins Rd, Suite 200A",
        "met_spending_threshold": True,
        "secondary_auditors_exist": False,
        "audit_period_other_months": "",
        "auditee_fiscal_period_end": "2021-06-30",
        "ein_not_an_ssn_attestation": True,
        "auditee_fiscal_period_start": "2020-07-01",
        "auditor_international_address": "",
        "user_provided_organization_type": "local",
        "auditor_ein_not_an_ssn_attestation": True,
    }

    sac_r1.federal_awards = {
        "Meta": {"section_name": "FederalAwardsExpended"},
        "FederalAwards": {
            "auditee_uei": "R5MQB3PSN2E3",
            "federal_awards": [
                {
                    "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                    "program": {
                        "is_major": "Y",
                        "program_name": "MORTGAGE INSURANCE FOR THE PURCHASE OR REFINANCING OF EXISTING MULTIFAMILY HOUSING PROJECTS",
                        "amount_expended": 1814238,
                        "audit_report_type": "U",
                        "federal_agency_prefix": "14",
                        "federal_program_total": 1814238,
                        "three_digit_extension": "155",
                        "number_of_audit_findings": 0,
                    },
                    "subrecipients": {"is_passed": "N"},
                    "award_reference": "AWARD-0001",
                    "loan_or_loan_guarantee": {
                        "is_guaranteed": "Y",
                        "loan_balance_at_audit_period_end": "1758128",
                    },
                    "direct_or_indirect_award": {"is_direct": "Y"},
                },
                {
                    "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                    "program": {
                        "is_major": "N",
                        "program_name": "SUPPORTIVE HOUSING FOR THE ELDERLY",
                        "amount_expended": 122505,
                        "federal_agency_prefix": "14",
                        "federal_program_total": 122505,
                        "three_digit_extension": "157",
                        "number_of_audit_findings": 0,
                    },
                    "subrecipients": {"is_passed": "N"},
                    "award_reference": "AWARD-0002",
                    "loan_or_loan_guarantee": {
                        "is_guaranteed": "Y",
                        "loan_balance_at_audit_period_end": "117445",
                    },
                    "direct_or_indirect_award": {"is_direct": "Y"},
                },
                {
                    "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                    "program": {
                        "is_major": "N",
                        "program_name": "SECTION 8 NEW CONSTRUCTION AND SUBSTANTIAL REHABILITATION",
                        "amount_expended": 272623,
                        "federal_agency_prefix": "14",
                        "federal_program_total": 272623,
                        "three_digit_extension": "182",
                        "number_of_audit_findings": 0,
                    },
                    "subrecipients": {"is_passed": "N"},
                    "award_reference": "AWARD-0003",
                    "loan_or_loan_guarantee": {"is_guaranteed": "N"},
                    "direct_or_indirect_award": {"is_direct": "Y"},
                },
            ],
            "total_amount_expended": 2209366,
        },
    }

    sac_r1.findings_uniform_guidance = {
        "Meta": {"section_name": "FindingsUniformGuidance"},
        "FindingsUniformGuidance": {
            "auditee_uei": "MCQEFMM2LJA4",
            "findings_uniform_guidance_entries": [
                {
                    "program": {
                        "award_reference": "AWARD-0008",
                        "compliance_requirement": "I",
                    },
                    "findings": {
                        "is_valid": "Y",
                        "prior_references": "N/A",
                        "reference_number": "2022-001",
                        "repeat_prior_reference": "N",
                    },
                    "other_matters": "Y",
                    "other_findings": "N",
                    "modified_opinion": "N",
                    "questioned_costs": "N",
                    "material_weakness": "Y",
                    "significant_deficiency": "N",
                },
                {
                    "program": {
                        "award_reference": "AWARD-0009",
                        "compliance_requirement": "I",
                    },
                    "findings": {
                        "is_valid": "Y",
                        "prior_references": "N/A",
                        "reference_number": "2022-001",
                        "repeat_prior_reference": "N",
                    },
                    "other_matters": "Y",
                    "other_findings": "N",
                    "modified_opinion": "N",
                    "questioned_costs": "N",
                    "material_weakness": "Y",
                    "significant_deficiency": "N",
                },
            ],
        },
    }

    sac_r1.save()

    sac_r2.general_information = {
        "ein": "316000427",
        "audit_type": "single-audit",
        "auditee_uei": "RHVRCYWNTFX3",
        "auditee_zip": "45177",
        "auditor_ein": "311334820",
        "auditor_zip": "43215",
        "auditee_city": "Wilmington",
        "auditee_name": "Clinton County",
        "auditor_city": "Columbus",
        "is_usa_based": True,
        "auditee_email": "habermehltg@clintoncountyohio.us",
        "auditee_phone": "9373822250",
        "auditee_state": "OH",
        "auditor_email": "dcf-southwest@ohioauditor.gov",
        "auditor_phone": "5133618550",
        "auditor_state": "OH",
        "auditor_country": "USA",
        "auditor_firm_name": "Ohio Auditor of State",
        "audit_period_covered": "annual",
        "auditee_contact_name": "Terence Habermehl",
        "auditor_contact_name": "Cristal Jones",
        "auditee_contact_title": "County Auditor",
        "auditor_contact_title": "Chief Auditor",
        "multiple_eins_covered": false,
        "multiple_ueis_covered": false,
        "auditee_address_line_1": "1850 David's Drive",
        "auditor_address_line_1": "88 East Broad Street",
        "met_spending_threshold": true,
        "secondary_auditors_exist": false,
        "audit_period_other_months": "",
        "auditee_fiscal_period_end": "2021-12-31",
        "ein_not_an_ssn_attestation": true,
        "auditee_fiscal_period_start": "2021-01-01",
        "auditor_international_address": "",
        "user_provided_organization_type": "local",
        "auditor_ein_not_an_ssn_attestation": true,
    }

    sac_r2.federal_awards = {
        "Meta": {"section_name": "FederalAwardsExpended"},
        "FederalAwards": {
            "auditee_uei": "JRRVW2KT4U71",
            "federal_awards": [
                {
                    "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                    "program": {
                        "is_major": "Y",
                        "program_name": "PROVIDER RELIEF FUND",
                        "amount_expended": 1709125,
                        "audit_report_type": "U",
                        "federal_agency_prefix": "93",
                        "federal_program_total": 1709125,
                        "three_digit_extension": "498",
                        "number_of_audit_findings": 1,
                    },
                    "subrecipients": {"is_passed": "N"},
                    "award_reference": "AWARD-0001",
                    "loan_or_loan_guarantee": {"is_guaranteed": "N"},
                    "direct_or_indirect_award": {"is_direct": "Y"},
                }
            ],
            "total_amount_expended": 1709125,
        },
    }

    sac_r2.save()

    # Make R3 the same as R1, but with one difference
    sac_r3 = SingleAuditChecklist.objects.get(report_id=rids["rid_3"])
    sac_r3.general_information = sac_r1.general_information | {
        "ein": "123456789",
    }
    # Simulate changing row 3
    sac_r3.federal_awards = deepcopy(sac_r1.federal_awards)
    sac_r3.federal_awards["FederalAwards"]["federal_awards"] = sac_r1.federal_awards[
        "FederalAwards"
    ]["federal_awards"][0:-1] + [
        {
            "cluster": {"cluster_name": "N/A", "cluster_total": 0},
            "program": {
                "is_major": "N",
                "program_name": "SECTION 8 NEW CONSTRUCTION AND SUBSTANTIAL REHABILITATION",
                "amount_expended": 1272623,
                "federal_agency_prefix": "14",
                "federal_program_total": 1272623,
                "three_digit_extension": "222",
                "number_of_audit_findings": 0,
            },
            "subrecipients": {"is_passed": "N"},
            "award_reference": "AWARD-0003",
            "loan_or_loan_guarantee": {"is_guaranteed": "N"},
            "direct_or_indirect_award": {"is_direct": "Y"},
        }
    ]
    sac_r3.federal_awards["FederalAwards"]["total_amount_expended"] = 3209366
    sac_r3.findings_uniform_guidance = deepcopy(sac_r1.findings_uniform_guidance)
    # Remove the last finding
    sac_r3.findings_uniform_guidance["FindingsUniformGuidance"][
        "findings_uniform_guidance_entries"
    ] = sac_r3.findings_uniform_guidance["FindingsUniformGuidance"][
        "findings_uniform_guidance_entries"
    ][
        0:-1
    ]

    sac_r3.save()


class CompareSubmissionTests(TestCase):

    def test_helpers(self):
        d1 = {"a": 1, "b": 2, "c": 3}
        d2 = {"a": 1, "b": 3, "d": 4}

        self.assertEqual(
            in_first_not_second(d1, d2), [{"key": "c", "from": 3, "to": None}]
        )

        self.assertEqual(
            in_second_not_first(d1, d2), [{"key": "d", "from": 4, "to": None}]
        )

        self.assertEqual(in_both(d1, d2), [{"key": "b", "from": 2, "to": 3}])

        self.assertEqual(
            analyze_pair(d1, d2),
            {
                "status": "changed",
                "in_r1": [{"key": "c", "from": 3, "to": None}],
                "in_r2": [{"key": "d", "from": 4, "to": None}],
                "in_both": [{"key": "b", "from": 2, "to": 3}],
            },
        )

    def test_getattrs(self):
        class TO:
            pass

        testObj = TO()
        deepObj = TO()
        deepObj.x = 16
        deepObj.y = 32

        deepDict = {}
        deepDict["g"] = 128
        deepDict["h"] = 256
        deepObj.d = deepDict

        testObj.a = 3
        testObj.b = 5
        testObj.deep = deepObj

        self.assertEqual(getattr_default(testObj, "b", 8), 5)
        self.assertEqual(getattr_default(testObj, "x", 8), 8)
        self.assertEqual(deep_getattr(testObj, ["deep", "x"], 8), 16)
        self.assertEqual(deep_getattr(testObj, ["deep", "z"], 8), 8)
        self.assertEqual(deep_getattr(testObj, ["deep", "d", "g"], 8), 128)
        self.assertEqual(deep_getattr(testObj, ["deep", "d", "z"], 8), 8)

    def test_compare_lists_of_objects(self):
        d1 = {"a": 1, "b": [{"name": "one", "value": 2}], "c": 3}
        d2 = {"a": 1, "b": [{"name": "two", "value": 3}], "d": 4}
        d3 = {
            "a": 1,
            "b": [{"name": "one", "value": 2}, {"name": "three", "value": 4}],
            "e": 5,
        }
        res = compare_lists_of_objects(d1, d2, ["b"], lambda o: o["value"])
        self.assertEqual(
            res, {"status": "changed", "in_r1": ["2"], "in_r2": ["3"], "in_both": []}
        )
        res = compare_lists_of_objects(d1, d3, ["b"], lambda o: o["value"])
        self.assertEqual(
            res, {"status": "changed", "in_r1": [], "in_r2": ["4"], "in_both": ["2"]}
        )

    def test_identical_sacs(self):
        setup_mock_db()
        summary = are_two_sacs_identical(
            "2025-01-FAKEDB-0000000001", "2025-01-FAKEDB-0000000001"
        )
        self.assertEqual(summary, True)

    def test_same_audit_no_change(self):
        setup_mock_db()
        # Comparing the same report should yield no change/difference.
        summary = compare_report_ids(
            "2025-01-FAKEDB-0000000001", "2025-01-FAKEDB-0000000001"
        )
        self.assertEqual("identical", summary.get("status", "should not get default"))

    def test_diff_audit_changes(self):
        # We should see that the status says "changed"
        # when sections are not the same
        setup_mock_db()

        summary = compare_report_ids(
            "2025-01-FAKEDB-0000000001", "2025-01-FAKEDB-0000000002"
        )

        self.assertEqual(
            "changed", summary.get("general_information", {}).get("status", None)
        )
        # Things changed from one to the other; there are no repeated values.
        self.assertEqual([], summary.get("general_information", {}).get("in_r1", None))
        self.assertEqual([], summary.get("general_information", {}).get("in_r2", None))
        # There should be a lot of things in the `in_both` key
        self.assertGreater(
            len(summary.get("general_information", {}).get("in_both", [])), 3
        )

    def test_one_difference(self):
        setup_mock_db()
        # We should see a difference of one field shows up in both r1 - r2 and r2 - r1.
        summary = compare_report_ids(
            "2025-01-FAKEDB-0000000001", "2025-01-FAKEDB-0000000003"
        )

        # There should be one key in both: ein
        self.assertEqual(
            1, len(summary.get("general_information", {}).get("in_both", {}))
        )
        # The "from" should be "370..." and the "to" should be "123..."
        self.assertEqual(
            "370906335",
            summary.get("general_information", {}).get("in_both", None)[0].get("from"),
        )
        self.assertEqual(
            "123456789",
            summary.get("general_information", {}).get("in_both", None)[0].get("to"),
        )

    # def test_federal_award_difference(self):
    #     # This should show us that an object *changed* between two reports.
    #     # Therefore, it will show up in r1 and r2.
    #     setup_mock_db()
    #     summary = compare_report_ids(
    #         "2025-01-FAKEDB-0000000001", "2025-01-FAKEDB-0000000003"
    #     )
    #     for key in ["in_r1", "in_r2"]:
    #         self.assertEqual(["AWARD-0003"], summary.get("federal_awards").get(key))

    # def test_findings_ug(self):
    #     # This shows us when something is missing in R2. It was present in R1, but
    #     # not in R2, so it only shows up in the R1 list. It also shows a compound-key
    #     # that is constructed from multiple parts of an object.
    #     setup_mock_db()
    #     summary = compare_report_ids(
    #         "2025-01-FAKEDB-0000000001", "2025-01-FAKEDB-0000000003"
    #     )

    #     self.assertEqual(
    #         ["AWARD-0009/2022-001"],
    #         summary.get("findings_uniform_guidance", {}).get("in_r1", None),
    #     )
    #     self.assertEqual(
    #         [],
    #         summary.get("findings_uniform_guidance", {}).get("in_r2", None),
    #     )
