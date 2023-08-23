# Even though the schemas are not Django views or modules etc., we test them
# here for CI/CD integration.
import json
import random
import string
from collections import deque
from random import choice, randrange

from django.conf import settings
from django.test import SimpleTestCase
from jsonschema import exceptions, validate as jsonschema_validate, FormatChecker

from audit.fixtures.excel import (
    ADDITIONAL_UEIS_TEST_FILE,
    CORRECTIVE_ACTION_PLAN_TEST_FILE,
    FEDERAL_AWARDS_TEST_FILE,
    FINDINGS_TEXT_TEST_FILE,
    FINDINGS_UNIFORM_GUIDANCE_TEST_FILE,
    SECONDARY_AUDITORS_TEST_FILE,
    NOTES_TO_SEFA_TEST_FILE,
    SIMPLE_CASES_TEST_FILE,
)

SECTION_SCHEMA_DIR = settings.SECTION_SCHEMA_DIR

# Simplest way to create a new copy of simple case rather than getting
# references to things used by other tests:


def jsoncopy(v):
    return json.loads(json.dumps(v))


def validate(instance, schema):
    """Wrap the validate function to include a format checker"""
    return jsonschema_validate(instance, schema, format_checker=FormatChecker())


class GeneralInformationSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the GeneralInformation JSON schema.
    """

    GENERAL_INFO_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "GeneralInformation.schema.json").read_text(
            encoding="utf-8"
        )
    )

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "GeneralInformationCase"
    ]

    def test_simple_pass(self):
        """
        The simple case should be valid
        """
        schema = self.GENERAL_INFO_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_invalid_auditee_fiscal_period_start(self):
        """
        If auditee_fiscal_period_start is an invalid date format, validation should fail
        """
        schema = self.GENERAL_INFO_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)

        bad_date = "not a date"
        simple_case["auditee_fiscal_period_start"] = bad_date

        self.assertRaisesRegex(
            exceptions.ValidationError,
            f"'{bad_date}' is not a 'date'",
            validate,
            simple_case,
            schema,
        )

    def test_invalid_auditee_fiscal_period_end(self):
        """
        If auditee_fiscal_period_end is an invalid date format, validation should fail
        """
        schema = self.GENERAL_INFO_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)

        bad_date = "not a date"
        simple_case["auditee_fiscal_period_end"] = bad_date

        self.assertRaisesRegex(
            exceptions.ValidationError,
            f"'{bad_date}' is not a 'date'",
            validate,
            simple_case,
            schema,
        )

    def test_null_auditee_name(self):
        """
        If the auditee_name is null, validation should pass
        """
        schema = self.GENERAL_INFO_SCHEMA
        instance = jsoncopy(self.SIMPLE_CASE)

        instance["auditee_name"] = None

        validate(instance, schema)

    def test_invalid_ein(self):
        """
        If the EIN is not in a valid format, validation should fail
        """
        schema = self.GENERAL_INFO_SCHEMA

        bad_eins = [
            f"{randrange(1000000000):010}",  # too long
            f"{randrange(10000000):08}",  # too short
            "".join(choice(string.ascii_letters) for i in range(9)),  # contains letters
            "".join(choice(string.punctuation) for i in range(9)),  # contains symbols
        ]

        for bad_ein in bad_eins:
            with self.subTest():
                instance = jsoncopy(self.SIMPLE_CASE)

                instance["ein"] = bad_ein

                with self.assertRaisesRegex(
                    exceptions.ValidationError,
                    "does not match",
                    msg=f"ValidationError not raised with EIN = {bad_ein}",
                ):
                    validate(instance, schema)

    def test_invalid_uei(self):
        """
        If the UEI is not in a valid format, validation should fail
        """
        schema = self.GENERAL_INFO_SCHEMA

        alpha_omit_oi = (
            string.ascii_letters.replace("i", "")
            .replace("I", "")
            .replace("o", "")
            .replace("O", "")
            .upper()  # We convert to uppercase in UEIValidationFormView.
        )
        good_uei = "".join(choice(alpha_omit_oi) for i in range(12))
        idx = randrange(12)

        too_short = "".join(choice(alpha_omit_oi) for i in range(11))
        too_long = "".join(choice(alpha_omit_oi) for i in range(13))
        zero_start = f"0{''.join(choice(alpha_omit_oi) for i in range(11))}"
        with_punc = good_uei[:idx] + choice(string.punctuation) + good_uei[idx + 1 :]
        with_numlike = good_uei[:idx] + choice("ioIO") + good_uei[idx + 1 :]
        with_commas = good_uei[:idx] + "," + good_uei[idx + 1 :]

        digits = "".join(choice(string.digits) for i in range(9))
        three_chars = "".join(choice(string.ascii_uppercase) for i in range(3))
        consecutive_base = deque(digits + three_chars)
        digits_start = "".join(consecutive_base)
        consecutive_base.rotate(1)
        digits_middle1 = "".join(consecutive_base)
        consecutive_base.rotate(1)
        digits_middle2 = "".join(consecutive_base)
        consecutive_base.rotate(1)
        digits_end = "".join(consecutive_base)

        bad_ueis_and_messages = [
            (too_short, f"'{too_short}' is too short"),
            (too_long, f"'{too_long}' is too long"),
            (zero_start, "does not match"),
            (with_punc, "does not match"),
            (with_commas, "does not match"),
            (with_numlike, "does not match"),
            (digits_start, "does not match"),
            (digits_middle1, "does not match"),
            (digits_middle2, "does not match"),
            (digits_end, "does not match"),
        ]

        for bad_uei, message in bad_ueis_and_messages:
            instance = jsoncopy(self.SIMPLE_CASE)
            instance["auditee_uei"] = bad_uei

            with self.subTest():
                with self.assertRaisesRegex(
                    exceptions.ValidationError,
                    message,
                    msg=f"ValidationError not raised with UEI = {bad_uei}",
                ):
                    validate(instance, schema)

    def test_valid_uei(self):
        """
        If the UEI is in a valid format, validation should pass
        """
        schema = self.GENERAL_INFO_SCHEMA

        alpha_omit_oi = (
            string.ascii_letters.replace("i", "")
            .replace("I", "")
            .replace("o", "")
            .replace("O", "")
            .upper()  # We convert to uppercase in UEIValidationFormView.
        )
        good_uei = "".join(choice(alpha_omit_oi) for i in range(12))

        instance = jsoncopy(self.SIMPLE_CASE)

        instance["auditee_uei"] = good_uei

        validate(instance, schema)

    # 2023-05-30: We're proceeding with the assumption that as a matter of
    # policy we can reject audits without UEIs. If that turns out to be untrue,
    # we'll uncomment these two tests.
    # def test_blank_uei(self):
    #     """
    #     If the UEI is an empty string, validation should pass
    #     """
    #     schema = self.GENERAL_INFO_SCHEMA
    #     instance = jsoncopy(self.SIMPLE_CASE)
    #
    #     instance["auditee_uei"] = ""
    #
    #     validate(instance, schema)
    #
    # def test_null_uei(self):
    #     """
    #     If the UEI is null, validation should pass
    #     """
    #     schema = self.GENERAL_INFO_SCHEMA
    #     instance = jsoncopy(self.SIMPLE_CASE)
    #
    #     instance["auditee_uei"] = None
    #
    #     validate(instance, schema)

    def test_invalid_zip(self):
        """
        If auditee_zip is not in a valid format, validation should fail
        """
        schema = self.GENERAL_INFO_SCHEMA

        bad_zips = [
            f"{randrange(1000000):06}",  # too long
            f"{randrange(10000):04}",  # too short
            "".join(choice(string.ascii_letters) for i in range(5)),  # contains letters
            "".join(choice(string.punctuation) for i in range(5)),  # contains symbols
        ]

        for zip_field in ["auditee_zip", "auditor_zip"]:
            for bad_zip in bad_zips:
                with self.subTest():
                    instance = jsoncopy(self.SIMPLE_CASE)

                    instance[zip_field] = bad_zip

                    with self.assertRaisesRegex(
                        exceptions.ValidationError,
                        "does not match",
                        msg=f"ValidationError not raised with zip = {bad_zip}",
                    ):
                        validate(instance, schema)

    def test_invalid_zip_plus_4(self):
        """
        If auditee_zip is not in a valid zip+4 format, validation should fail
        """
        schema = self.GENERAL_INFO_SCHEMA

        # generate a valid 5 digit zip code
        valid_zip = f"{randrange(100000):05}"

        # append invalid +4 suffixes
        bad_zips = [
            f"{valid_zip}-{randrange(10000):05}",  # +4 too long
            f"{valid_zip}-{randrange(1000):03}",  # +4 too short
            # contains letters
            f"{valid_zip}-{''.join(choice(string.ascii_letters) for i in range(4))}",
            # contains symbols
            f"{valid_zip}-{''.join(choice(string.punctuation) for i in range(4))}",
        ]

        for zip_field in ["auditee_zip", "auditor_zip"]:
            for bad_zip in bad_zips:
                with self.subTest():
                    instance = jsoncopy(self.SIMPLE_CASE)

                    instance[zip_field] = bad_zip

                    with self.assertRaisesRegex(
                        exceptions.ValidationError,
                        "does not match",
                        msg=f"ValidationError not raised with zip = {bad_zip}",
                    ):
                        validate(instance, schema)

    def test_valid_phone(self):
        """
        If auditee_phone is in a valid format, validation should pass
        """
        schema = self.GENERAL_INFO_SCHEMA

        good_phones_wo_country_code = [
            f"{randrange(10000000000):010}",  # e.g. 5555555555
            # e.g. 555-555-5555
            f"{randrange(1000):03}-{randrange(1000):03}-{randrange(10000):04}",
            # e.g. 555.555.5555
            f"{randrange(1000):03}.{randrange(1000):03}.{randrange(10000):04}",
            # e.g. 555 555 5555
            f"{randrange(1000):03} {randrange(1000):03} {randrange(10000):04}",
            # e.g. (555)-555-5555
            f"({randrange(1000):03})-{randrange(1000):03}-{randrange(10000):04}",
            # e.g. (555).555.5555
            f"({randrange(1000):03}).{randrange(1000):03}.{randrange(10000):04}",
            # e.g. (555) 555 5555
            f"({randrange(1000):03}) {randrange(1000):03} {randrange(10000):04}",
        ]

        good_phones_w_country_code = [f"+1 {p}" for p in good_phones_wo_country_code]

        good_phones = good_phones_wo_country_code + good_phones_w_country_code

        for phone_field in ["auditee_phone", "auditor_phone"]:
            for good_phone in good_phones:
                with self.subTest():
                    instance = jsoncopy(self.SIMPLE_CASE)

                    instance[phone_field] = good_phone

                    validate(instance, schema)

    def test_invalid_phone(self):
        """
        If auditee_phone is not in a valid format, validation should fail
        """
        schema = self.GENERAL_INFO_SCHEMA

        bad_phones = [
            f"{randrange(100000000):09}",  # too short
            f"{randrange(10000000000):011}",  # too long
            "".join(
                choice(string.ascii_letters) for i in range(10)
            ),  # contains letters
        ]

        for phone_field in ["auditee_phone", "auditor_phone"]:
            for bad_phone in bad_phones:
                with self.subTest():
                    instance = jsoncopy(self.SIMPLE_CASE)

                    instance[phone_field] = bad_phone

                    with self.assertRaisesRegex(
                        exceptions.ValidationError,
                        "does not match",
                        msg=f"ValidationError not raised with phone = {bad_phone}",
                    ):
                        validate(instance, schema)


class AuditInformationSchemaValidityTest(SimpleTestCase):
    AUDIT_INFO_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "AuditInformation.schema.json").read_text(
            encoding="utf-8"
        )
    )

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "AuditInformationCases"
    ]

    def test_schema(self):
        """Try to test Audit Info schema."""
        schema = self.AUDIT_INFO_SCHEMA
        validate(self.SIMPLE_CASE[0], schema)

    def test_all_booleans(self):
        schema = self.AUDIT_INFO_SCHEMA
        simple_case = jsoncopy(self.SIMPLE_CASE[0])

        boolean_fields = [
            "is_going_concern_included",
            "is_internal_control_deficiency_disclosed",
            "is_internal_control_material_weakness_disclosed",
            "is_material_noncompliance_disclosed",
            "is_aicpa_audit_guide_included",
            "is_low_risk_auditee",
        ]
        for value in [True, False]:
            for field in boolean_fields:
                simple_case[field] = value
                validate(simple_case, schema)

    def test_all_gaap_results(self):
        schema = self.AUDIT_INFO_SCHEMA
        simple_case = jsoncopy(self.SIMPLE_CASE[0])
        gaap_results = [
            "unmodified_opinion",
            "qualified_opinion",
            "adverse_opinion",
            "disclaimer_of_opinion",
        ]

        for _ in range(10):
            for n in range(2, 5):
                ls = random.sample(gaap_results, n)
                simple_case["gaap_results"] = ls
                validate(simple_case, schema)

        # Test when it is 'not_gaap', which requires other fields.
        simple_case["gaap_results"] = ["not_gaap"]
        simple_case["is_sp_framework_required"] = random.choice([True, False])
        simple_case["sp_framework_basis"] = random.choices(
            ["cash_basis", "tax_basis", "contractual_basis", "other_basis"], k=2
        )
        simple_case["sp_framework_opinions"] = random.choices(
            [
                "unmodified_opinion",
                "qualified_opinion",
                "adverse_opinion",
                "disclaimer_of_opinion",
            ],
            k=2,
        )
        validate(simple_case, schema)

    def test_bad_gaap_results(self):
        schema = self.AUDIT_INFO_SCHEMA
        simple_case = jsoncopy(self.SIMPLE_CASE[0])
        not_gaap_values = [
            "state",
            "local",
            "tribal",
            "higher-ed",
            "non-profit",
            "unknown",
            "none",
        ]

        for word in not_gaap_values:
            simple_case["gaap_results"] = [word]
            self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_bad_sp_framework_opinions(self):
        schema = self.AUDIT_INFO_SCHEMA
        simple_case = jsoncopy(self.SIMPLE_CASE[1])

        simple_case["sp_framework_opinions"] = "not_a_real_opinion"
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_bad_sp_framework_basis(self):
        schema = self.AUDIT_INFO_SCHEMA
        simple_case = jsoncopy(self.SIMPLE_CASE[1])

        simple_case["sp_framework_basis"] = "an_invalid_basis"
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_valid_aln_prefixes(self):
        schema = self.AUDIT_INFO_SCHEMA
        simple_case = jsoncopy(self.SIMPLE_CASE[0])
        # Why "likely?" I have no idea what is authoritative.
        # Fix the tests as we discover changes, and update the
        # validation schema while we're at it.
        likely_valid_aln_prefixes = [
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "27",
            "29",
            "30",
            "32",
            "33",
            "34",
            "36",
            "39",
            "40",
            "41",
            "42",
            "43",
            "44",
            "45",
            "46",
            "47",
            "53",
            "57",
            "58",
            "59",
            "60",
            "61",
            "62",
            "64",
            "66",
            "68",
            "70",
            "77",
            "78",
            "81",
            "82",
            "83",
            "84",
            "85",
            "86",
            "87",
            "88",
            "89",
            "90",
            "91",
            "92",
            "93",
            "94",
            "96",
            "97",
            "98",
            "99",
        ]

        for _ in range(10):
            for n in range(2, 10):
                ls = random.sample(likely_valid_aln_prefixes, n)
                simple_case["agencies"] = ls
                validate(simple_case, schema)


class FederalAwardsSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the FederalAwards JSON schema.
    """

    FEDERAL_AWARDS_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "FederalAwards.schema.json").read_text(encoding="utf-8")
    )

    SIMPLE_CASES = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "FederalAwardsCases"
    ]

    def test_schema(self):
        """Try to test FederalAwards first."""
        schema = self.FEDERAL_AWARDS_SCHEMA

        in_flight_file = FEDERAL_AWARDS_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest Federal Award case; none of the conditional fields
        apply.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        validate(self.SIMPLE_CASES[0], schema)

    def test_missing_auditee_uei(self):
        """
        Test that validation fails if auditee_uei is missing
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])
        del simple_case["FederalAwards"]["auditee_uei"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_total_amount_expended(self):
        """
        Test that validation fails if total_amount_expended is missing
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])
        del simple_case["FederalAwards"]["total_amount_expended"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_simple_fail_with_extraneous(self):
        """
        Test the simplest Federal Award case; none of the conditional fields
        apply but we're giving answers for them anyway
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])

        simple_case["FederalAwards"]["federal_awards"][0][
            "loan_balance_at_audit_period_end"
        ] = 10_000
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_loan_dependents(self):
        """
        If loan_or_loan_guarantee is Y, loan_balance_at_audit_period_end must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[1])
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_int_pass = award | {
            "loan_or_loan_guarantee": {
                "is_guaranteed": "Y",
                "loan_balance_at_audit_period_end": 10_000,
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_int_pass]

        validate(simple_case, schema)

        for valid in ["", "null", 0]:
            both_na_pass = award | {
                "loan_or_loan_guarantee": {
                    "is_guaranteed": "N",
                    "loan_balance_at_audit_period_end": valid,
                }
            }
            simple_case["FederalAwards"]["federal_awards"] = [both_na_pass]

            validate(simple_case, schema)

        no_dependent_fail = award | {"loan_or_loan_guarantee": {"is_guaranteed": "Y"}}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {
            "loan_or_loan_guarantee": {"loan_balance_at_audit_period_end": 10_000}
        }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_value_fail = award | {
            "loan_or_loan_guarantee": {
                "is_guaranteed": "Y",
                "loan_balance_at_audit_period_end": "not applicable",
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_value_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        zero_value_fail = award | {
            "loan_or_loan_guarantee": {
                "is_guaranteed": "Y",
                "loan_balance_at_audit_period_end": 0,
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [zero_value_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_direct_award_dependents(self):
        """
        direct_or_indirect_award tests
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[1])
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        # 20230408 MCJ
        # In Python, the `|` is a dictionary union operator. Python 3.9
        # https://betterprogramming.pub/new-union-operators-to-merge-dictionaries-in-python-3-9-8c7dbbd1080c
        both_pass = award | {
            "direct_or_indirect_award": {
                "is_direct": "N",
                "entities": [
                    {
                        "passthrough_name": "Bob",
                        "passthrough_identifying_number": "Bob-123",
                    }
                ],
            },
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        no_dependent_fail = award | {"direct_or_indirect_award": {"is_direct": "N"}}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {
            "direct_or_indirect_award": {
                "entities": [
                    {
                        "passthrough_name": "Bob",
                        "passthrough_identifying_number": "Bob-123",
                    }
                ]
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_entity_fail = award | {
            "direct_or_indirect_award": {
                "is_direct": "N",
                "entities": [{"passthrough_name": "Bob"}],
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_entity_fail]
        validate(simple_case, schema)

        bad_entity_empty_fail = award | {
            "direct_or_indirect_award": {
                "is_direct": "N",
                "entities": [
                    {"passthrough_name": "Bob", "passthrough_identifying_number": ""}
                ],
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_entity_empty_fail]
        validate(simple_case, schema)

    def test_passthrough_dependents(self):
        """
        If federal_award_passed_to_subrecipients is Y,
        federal_award_passed_to_subrecipients_amount must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_pass = award | {
            "subrecipients": {"is_passed": "Y", "subrecipient_amount": 10_000}
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        no_dependent_fail = award | {"subrecipients": {"is_passed": "Y"}}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {"subrecipients": {"subrecipient_amount": 10_000}}
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_major_program_dependents(self):
        """
        If major_program is Y, major_program_audit_report_type must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_pass = award | {
            "program": {
                "federal_agency_prefix": "42",
                "three_digit_extension": "123",
                "program_name": "Bob",
                "is_major": "Y",
                "audit_report_type": "U",
                "number_of_audit_findings": 0,
                "amount_expended": 42,
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        invalid_fail = award | {
            "program": {
                "federal_agency_prefix": "42",
                "three_digit_extension": "123",
                "program_name": "Bob",
                "is_major": "Y",
                "number_of_audit_findings": 0,
                "amount_expended": 42,
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [invalid_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        no_dependent_fail = award | {"is_major": "Y"}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {
            "audit_report_type": "U",
        }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_state_cluster_name(self):
        """
        state_cluster_name tests
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])

        simple_case["FederalAwards"]["federal_awards"][0]["cluster"][
            "cluster_name"
        ] = "STATE CLUSTER"
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_disallowed_state_cluster_name(self):
        """
        If cluster name is not 'STATE CLUSTER', state_cluster_name must be empty or null
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])
        simple_case["FederalAwards"]["federal_awards"][0]["cluster"][
            "state_cluster_name"
        ] = "ANYTHING"

        # Test for errors when state_cluster_name is not empty or null
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        # Test for successful validation when state_cluster_name is empty or null
        for valid in ["", "null"]:
            simple_case = jsoncopy(self.SIMPLE_CASES[0])
            simple_case["FederalAwards"]["federal_awards"][0]["cluster"][
                "state_cluster_name"
            ] = valid

            validate(simple_case, schema)

    def test_number_of_audit_findings(self):
        """
        If major_program_audit_report_type is A or Q, number_of_audit_findings must be greater than 0
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASES[0])
        simple_case["FederalAwards"]["federal_awards"][0]["program"]["is_major"] = "Y"

        for report_type in ["A", "Q"]:
            # major_audit_report_type of A or Q requires non-zero number_of_audit_findings
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "audit_report_type"
            ] = report_type
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = 0
            # We cannot find, in the UG, anything that suggests this is true.
            # This seems like it should be allowed to pass.
            # self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)
            validate(simple_case, schema)

            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = 1
            validate(simple_case, schema)

        for report_type in ["U", "D"]:
            # major_audit_report_type of U or D can be zero or greater
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "audit_report_type"
            ] = report_type
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = 0
            validate(simple_case, schema)

            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = random.randint(1, 100)
            validate(simple_case, schema)


class CorrectiveActionPlanSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the CorrectiveActionPlan JSON schema.
    """

    CORRECTIVE_ACTION_PLAN_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "CorrectiveActionPlan.schema.json").read_text(
            encoding="utf-8"
        )
    )

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "CorrectiveActionPlanCase"
    ]

    def test_schema(self):
        """Try to test CorrectiveActionPlan first."""
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        in_flight_file = CORRECTIVE_ACTION_PLAN_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest Corrective Action Plan case; none of the conditional fields
        apply.
        """
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_uei(self):
        """
        Test that validation fails if auditee_uei is missing
        """
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["CorrectiveActionPlan"]["auditee_uei"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_entry_fields(self):
        """
        Test that validation fails if any entry field is missing
        """
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["CorrectiveActionPlan"]["corrective_action_plan_entries"][0][
            "contains_chart_or_table"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["CorrectiveActionPlan"]["corrective_action_plan_entries"][0][
            "planned_action"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["CorrectiveActionPlan"]["corrective_action_plan_entries"][0][
            "reference_number"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_empty_entry_fields(self):
        """
        Test that validation fails if any entry field is empty
        """
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["CorrectiveActionPlan"]["corrective_action_plan_entries"][0][
            "contains_chart_or_table"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["CorrectiveActionPlan"]["corrective_action_plan_entries"][0][
            "planned_action"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["CorrectiveActionPlan"]["corrective_action_plan_entries"][0][
            "reference_number"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_for_invalid_entry(self):
        """
        Test that validation fails if invalid value is provided for entry field
        """
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["CorrectiveActionPlan"]["corrective_action_plan_entries"][0][
            "contains_chart_or_table"
        ] = 0
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)


class FindingsTextSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the FindingsText JSON schema.
    """

    FINDINGS_TEXT_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "AuditFindingsText.schema.json").read_text(
            encoding="utf-8"
        )
    )

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "FindingsTextCase"
    ]

    def test_schema(self):
        """Try to test FindingsText first."""
        schema = self.FINDINGS_TEXT_SCHEMA

        in_flight_file = FINDINGS_TEXT_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest FindingsText case; none of the conditional fields apply.
        """
        schema = self.FINDINGS_TEXT_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_uei(self):
        """
        Test that validation fails if auditee_uei is missing
        """
        schema = self.FINDINGS_TEXT_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsText"]["auditee_uei"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_entry_fields(self):
        """
        Test that validation fails if any entry field is missing
        """
        schema = self.FINDINGS_TEXT_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsText"]["findings_text_entries"][0][
            "contains_chart_or_table"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsText"]["findings_text_entries"][0]["text_of_finding"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsText"]["findings_text_entries"][0]["reference_number"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_empty_entry_fields(self):
        """
        Test that validation fails if any entry field is empty
        """
        schema = self.FINDINGS_TEXT_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsText"]["findings_text_entries"][0][
            "contains_chart_or_table"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsText"]["findings_text_entries"][0][
            "text_of_finding"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsText"]["findings_text_entries"][0][
            "reference_number"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_for_invalid_entry(self):
        """
        Test that validation fails if invalid value is provided for entry field
        """
        schema = self.FINDINGS_TEXT_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsText"]["findings_text_entries"][0][
            "contains_chart_or_table"
        ] = 0
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)


class AdditionalUeisSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the AdditionalUEIs JSON schema.
    """

    ADDITIONAL_UEIS_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "AdditionalUEIs.schema.json").read_text(encoding="utf-8")
    )

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "AdditionalUeisCase"
    ]

    def test_schema(self):
        """Test AdditionalUEIs schema first."""
        schema = self.ADDITIONAL_UEIS_SCHEMA

        in_flight_file = ADDITIONAL_UEIS_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test a simple AdditionalUEIs case.
        """
        schema = self.ADDITIONAL_UEIS_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_uei(self):
        """
        Test that validation fails if auditee_uei is missing
        """
        schema = self.ADDITIONAL_UEIS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["AdditionalUEIs"]["auditee_uei"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_entry_fields(self):
        """
        Test that validation fails if any entry field is missing
        """
        schema = self.ADDITIONAL_UEIS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["AdditionalUEIs"]["additional_ueis_entries"][0][
            "additional_uei"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_empty_entry_fields(self):
        """
        Test that validation fails if any entry field is empty
        """
        schema = self.ADDITIONAL_UEIS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["AdditionalUEIs"]["additional_ueis_entries"][0][
            "additional_uei"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_for_invalid_entry(self):
        """
        Test that validation fails if invalid value is provided for entry field
        """
        schema = self.ADDITIONAL_UEIS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["AdditionalUEIs"]["additional_ueis_entries"][0][
            "additional_uei"
        ] = 123456789
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)


class NotesToSefaSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the NotesToSefa JSON schema.
    """

    NOTES_TO_SEFA_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "NotesToSefa.schema.json").read_text(encoding="utf-8")
    )
    SIMPLE_CASES = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "NotesToSefaCases"
    ]

    SIMPLE_CASE = SIMPLE_CASES[0]

    def test_schema(self):
        """Test NotesToSefa schema first."""
        schema = self.NOTES_TO_SEFA_SCHEMA
        in_flight_file = NOTES_TO_SEFA_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test a simple NotesToSefa case.
        One with notes, one without
        """
        schema = self.NOTES_TO_SEFA_SCHEMA
        validate(self.SIMPLE_CASE, schema)
        validate(self.SIMPLE_CASES[1], schema)

    def test_missing_auditee_uei(self):
        """
        Test that validation fails when auditee_uei is missing
        """
        schema = self.NOTES_TO_SEFA_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["NotesToSefa"]["auditee_uei"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_entry_fields(self):
        """
        Test that validation fails if any required entry field is missing
        """
        schema = self.NOTES_TO_SEFA_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        validate(simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["NotesToSefa"]["accounting_policies"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["NotesToSefa"]["notes_to_sefa_entries"][0]["note_title"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_for_invalid_entry(self):
        """
        Test that validation fails if invalid value is provided for entry field
        """
        schema = self.NOTES_TO_SEFA_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["NotesToSefa"]["auditee_uei"] = 123456789
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)


class FindingsUniformGuidanceSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the FindingsUniformGuidance JSON schema.
    """

    FINDINGS_UNIFORM_GUIDANCE_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "FederalAwardsAuditFindings.schema.json").read_text(
            encoding="utf-8"
        )
    )

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "FindingsUniformGuidanceCase"
    ]

    def test_schema(self):
        """Try to test FindingsUniformGuidance first."""
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        in_flight_file = FINDINGS_UNIFORM_GUIDANCE_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))

        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest FindingsUniformGuidance case; none of the conditional fields
        apply.
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_uei(self):
        """
        Test that validation fails if auditee_uei is missing
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["auditee_uei"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_entry_fields(self):
        """
        Test that validation fails if any entry field is missing
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["program"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["findings"]["prior_references"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["significant_deficiency"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["other_matters"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["other_findings"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["modified_opinion"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["material_weakness"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][
            0
        ]["findings"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_empty_entry_fields(self):
        """
        Test that validation fails if any entry field is empty
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "program"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "findings"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "significant_deficiency"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "other_matters"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "other_findings"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "modified_opinion"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "material_weakness"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "findings"
        ]["prior_references"] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_for_invalid_entry(self):
        """
        Test that validation fails if any entry field is invalid
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "significant_deficiency"
        ] = 0
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "other_matters"
        ] = 0
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "other_findings"
        ] = "invalid"
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "modified_opinion"
        ] = "invalid"
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "material_weakness"
        ] = "invalid"
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "findings"
        ]["is_valid"] = 0
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)


class SecondaryAuditorsSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the SecondaryAuditors JSON schema.
    """

    SECONDARY_AUDITORS_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "SecondaryAuditors.schema.json").read_text(
            encoding="utf-8"
        )
    )

    SIMPLE_CASE = json.loads(SIMPLE_CASES_TEST_FILE.read_text(encoding="utf-8"))[
        "SecondaryAuditorsCase"
    ]

    def test_schema(self):
        """Try to test SecondaryAuditors first."""
        schema = self.SECONDARY_AUDITORS_SCHEMA

        in_flight_file = SECONDARY_AUDITORS_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest SecondaryAuditors case; none of the conditional fields apply.
        """
        schema = self.SECONDARY_AUDITORS_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_ein(self):
        """
        Test that validation fails if auditee_uei is missing
        """
        schema = self.SECONDARY_AUDITORS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["SecondaryAuditors"]["auditee_uei"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_entry_fields(self):
        """
        Test that validation fails if an entry field is missing
        """
        schema = self.SECONDARY_AUDITORS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["SecondaryAuditors"]["secondary_auditors_entries"][0][
            "secondary_auditor_ein"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_empty_entry_fields(self):
        """
        Test that validation fails if ay entry field is empty
        """
        schema = self.SECONDARY_AUDITORS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["SecondaryAuditors"]["secondary_auditors_entries"][0][
            "secondary_auditor_address_state"
        ] = None
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_for_invalid_entry(self):
        """
        Test that validation fails if invalid value is provided for entry field
        """
        schema = self.SECONDARY_AUDITORS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["SecondaryAuditors"]["secondary_auditors_entries"][0][
            "secondary_auditor_name"
        ] = []
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)
