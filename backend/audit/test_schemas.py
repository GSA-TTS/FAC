# Even though the schemas are not Django views or modules etc., we test them
# here for CI/CD integration.
import json
import string

from pathlib import Path
from django.test import SimpleTestCase
from jsonschema import exceptions, validate as jsonschema_validate, FormatChecker
from random import choice, randrange

from audit.fixtures.excel import CORRECTIVE_ACTION_PLAN_TEST_FILE, FINDINGS_UNIFORM_GUIDANCE_TEST_FILE

# Simplest way to create a new copy of simple case rather than getting
# references to things used by other tests:
jsoncopy = lambda v: json.loads(json.dumps(v))


# wrap the validate function to include a format checker
def validate(instance, schema):
    return jsonschema_validate(instance, schema, format_checker=FormatChecker())


# 20230408 MCJ FIXME: This path is encoded in multiple places.
# Why isn't it encoded once in settings.py?
SCHEMA_DIR = Path(__file__).parent.parent / "schemas"
SECTION_SCHEMA_DIR = Path(__file__).parent.parent / "schemas" / "sections"


class GeneralInformationSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the GeneralInformation JSON schema.
    """

    GENERAL_INFO_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "GeneralInformation.schema.json").read_text(encoding="utf-8")
    )

    SIMPLE_CASE = {
        "auditee_fiscal_period_start": "2022-01-01",
        "auditee_fiscal_period_end": "2022-12-31",
        "audit_period_covered": "annual",
        "ein": "123456789",
        "ein_not_an_ssn_attestation": True,
        "multiple_eins_covered": False,
        "auditee_uei": "1A2B3C4D5E6F",
        "multiple_ueis_covered": False,
        "auditee_name": "John",
        "auditee_address_line_1": "123 Fake St.",
        "auditee_city": "FakeCity",
        "auditee_state": "AL",
        "auditee_zip": "12345",
        "auditee_contact_name": "John",
        "auditee_contact_title": "A Title",
        "auditee_phone": "555-555-5555",
        "auditee_email": "john@test.test",
        "user_provided_organization_type": "state",
        "met_spending_threshold": True,
        "is_usa_based": True,
        "auditor_firm_name": "Firm LLC",
        "auditor_ein": "123456789",
        "auditor_ein_not_an_ssn_attestation": True,
        "auditor_country": "USA",
        "auditor_address_line_1": "456 Fake St.",
        "auditor_city": "AnotherFakeCity",
        "auditor_state": "WY",
        "auditor_zip": "56789",
        "auditor_contact_name": "Jane",
        "auditor_contact_title": "Another Title",
        "auditor_phone": "999-999-9999",
        "auditor_email": "jane@test.test",
    }

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

                self.assertRaisesRegex(
                    exceptions.ValidationError,
                    "does not match",
                    validate,
                    instance,
                    schema,
                )

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
        )
        good_uei = "".join(choice(alpha_omit_oi) for i in range(12))
        idx = randrange(12)

        with_punc = good_uei[:idx] + choice(string.punctuation) + good_uei[idx + 1 :]
        with_ioIO = good_uei[:idx] + choice("ioIO") + good_uei[idx + 1 :]

        bad_ueis = [
            "".join(choice(alpha_omit_oi) for i in range(11)),  # too short
            "".join(choice(alpha_omit_oi) for i in range(13)),  # too long
            f"0{''.join(choice(alpha_omit_oi) for i in range(11))}",  # starts with 0
            with_punc,  # contains a non-alphanum char
            with_ioIO,  # contains one of i, o, I, O
        ]

        for bad_uei in bad_ueis:
            with self.subTest():
                instance = jsoncopy(self.SIMPLE_CASE)

                instance["auditee_uei"] = bad_uei

                self.assertRaisesRegex(
                    exceptions.ValidationError,
                    "does not match",
                    validate,
                    instance,
                    schema,
                )

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
        )
        good_uei = "".join(choice(alpha_omit_oi) for i in range(12))

        instance = jsoncopy(self.SIMPLE_CASE)

        instance["auditee_uei"] = good_uei

        validate(instance, schema)

    def test_blank_uei(self):
        """
        If the UEI is an empty string, validation should pass
        """
        schema = self.GENERAL_INFO_SCHEMA
        instance = jsoncopy(self.SIMPLE_CASE)

        instance["auditee_uei"] = ""

        validate(instance, schema)

    def test_null_uei(self):
        """
        If the UEI is null, validation should pass
        """
        schema = self.GENERAL_INFO_SCHEMA
        instance = jsoncopy(self.SIMPLE_CASE)

        instance["auditee_uei"] = None

        validate(instance, schema)

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

                    self.assertRaisesRegex(
                        exceptions.ValidationError,
                        "does not match",
                        validate,
                        instance,
                        schema,
                    )

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
            f"{valid_zip}-{''.join(choice(string.ascii_letters) for i in range(4))}",  # contains letters
            f"{valid_zip}-{''.join(choice(string.punctuation) for i in range(4))}",  # contains symbols
        ]

        for zip_field in ["auditee_zip", "auditor_zip"]:
            for bad_zip in bad_zips:
                with self.subTest():
                    instance = jsoncopy(self.SIMPLE_CASE)

                    instance[zip_field] = bad_zip

                    self.assertRaisesRegex(
                        exceptions.ValidationError,
                        "does not match",
                        validate,
                        instance,
                        schema,
                    )

    def test_valid_phone(self):
        """
        If auditee_phone is in a valid format, validation should pass
        """
        schema = self.GENERAL_INFO_SCHEMA

        good_phones_wo_country_code = [
            f"{randrange(10000000000):010}",  # e.g. 5555555555
            f"{randrange(1000):03}-{randrange(1000):03}-{randrange(10000):04}",  # e.g. 555-555-5555
            f"{randrange(1000):03}.{randrange(1000):03}.{randrange(10000):04}",  # e.g. 555.555.5555
            f"{randrange(1000):03} {randrange(1000):03} {randrange(10000):04}",  # e.g. 555 555 5555
            f"({randrange(1000):03})-{randrange(1000):03}-{randrange(10000):04}",  # e.g. (555)-555-5555
            f"({randrange(1000):03}).{randrange(1000):03}.{randrange(10000):04}",  # e.g. (555).555.5555
            f"({randrange(1000):03}) {randrange(1000):03} {randrange(10000):04}",  # e.g. (555) 555 5555
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

                    self.assertRaisesRegex(
                        exceptions.ValidationError,
                        "does not match",
                        validate,
                        instance,
                        schema,
                    )


class FederalAwardsSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the FederalAwards JSON schema.
    """

    FEDERAL_AWARDS_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "FederalAwards.schema.json").read_text(encoding="utf-8")
    )

    # SIMPLE_CASE = {
    #     "FederalAwards": {
    #         "auditee_ein": "12345678",
    #         "total_amount_expended": 0,
    #         "federal_awards": [
    #             {
    #                 "program_number": "10.001",
    #                 "federal_program_name": "GACC",
    #                 "amount_expended": 0,
    #                 "cluster_name": "N/A",
    #                 "loan_or_loan_guarantee": "N",
    #                 "direct_award": "Y",
    #                 "federal_award_passed_to_subrecipients": "N",
    #                 "major_program": "N",
    #                 "number_of_audit_findings": 0,
    #             }
    #         ],
    #     }
    # }

    SIMPLE_CASE = {
        "FederalAwards": {
            "auditee_ein": None,
            "total_amount_expended": 12345,
            "federal_awards": [
                {
                    "program": {
                        "name": "Bob",
                        "number": "42.123",
                        "is_major": "N",
                        "audit_report_type": "",
                        "number_of_audit_findings": 0,
                        "amount_expended": 42
                    },
                    "loan_or_loan_guarantee": {
                        "is_guaranteed": "N",
                        "loan_balance_at_audit_period_end": 0
                    },
                    "direct_or_indirect_award": {
                    "is_direct": "N",
                    "entities": [
                        {
                            "name": "Bob's Granting House",
                            "identifying_number": "12345"
                        }
                    ]
                    },
                    "cluster": {
                        "name": "N/A",
                        "total": 123
                    },
                    "subrecipients": {
                        "is_passed": "N"
                    },
                }
            ]
        }
    }

    M1 = {
        "FederalAwards": {
            "auditee_ein": None,
            "total_amount_expended": 12345,
            "federal_awards": [
                {
                    "program": {
                        "name": "Bob",
                        "number": "42.123",
                        "is_major": "Y",
                        "audit_report_type": "U",
                        "number_of_audit_findings": 0,
                        "amount_expended": 42
                    },
                    "loan_or_loan_guarantee": {
                        "is_guaranteed": "Y",
                        "loan_balance_at_audit_period_end": 42
                    },
                    "direct_or_indirect_award": {
                        "is_direct": "Y",
                        "entities": []
                    },
                    "subrecipients": {
                        "is_passed": "Y",
                        "amount": 32
                    },
                    "cluster": {
                        "name": "STATE CLUSTER",
                        "total": 123,
                        "state_cluster_name": "Maine"
                    }
                }
            ]
        }
    }

    def test_schema(self):
        """Try to test FederalAwards first."""
        schema = self.FEDERAL_AWARDS_SCHEMA
        # 20230408 MCJ FIXME : Paths!
        for f in [
            "federalawards-pass-01.json"
            ]:
            in_flight_file = SCHEMA_DIR / "test-files" / f
            in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
            validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest Federal Award case; none of the conditional fields
        apply.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_ein(self):
        """
        Test that validation fails if auditee_ein is missing
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FederalAwards"]["auditee_ein"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_total_amount_expended(self):
        """
        Test that validation fails if total_amount_expended is missing
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FederalAwards"]["total_amount_expended"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_simple_fail_with_extraneous(self):
        """
        Test the simplest Federal Award case; none of the conditional fields
        apply but we're giving answers for them anyway
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)

        simple_case["FederalAwards"]["federal_awards"][0][
            "loan_balance_at_audit_period_end"
        ] = 10_000
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_loan_dependents(self):
        """
        If loan_or_loan_guarantee is Y, loan_balance_at_audit_period_end must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.M1)
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_int_pass = award | {
            "loan_or_loan_guarantee": {
                "is_guaranteed": "Y",
                "loan_balance_at_audit_period_end": 10_000
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_int_pass]

        validate(simple_case, schema)

        for valid in ["", 'null', 0]:
            both_na_pass = award | {
                "loan_or_loan_guarantee": {
                    "is_guaranteed": "N",
                    "loan_balance_at_audit_period_end": valid
                }
            }
            simple_case["FederalAwards"]["federal_awards"] = [both_na_pass]

            validate(simple_case, schema)

        no_dependent_fail = award | {
            "loan_or_loan_guarantee": {
                "is_guaranteed": "Y"
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {
            "loan_or_loan_guarantee": {
                "loan_balance_at_audit_period_end": 10_000
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_value_fail = award | {
            "loan_or_loan_guarantee": {
                "is_guaranteed": "Y",
                "loan_balance_at_audit_period_end": "not applicable"
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_value_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        zero_value_fail = award | {
            "loan_or_loan_guarantee": {
                "is_guaranteed": "Y",
                "loan_balance_at_audit_period_end": 0
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [zero_value_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_direct_award_dependents(self):
        """
        If direct_award is Y, loan_balance_at_audit_period_end must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        # 20230408 MCJ
        # In Python, the `|` is a dictionary union operator. Python 3.9
        # https://betterprogramming.pub/new-union-operators-to-merge-dictionaries-in-python-3-9-8c7dbbd1080c
        both_pass = award | {
            "direct_or_indirect_award": {
                "is_direct": "N",
                "entities": [{"name": "Bob", "identifying_number": "Bob-123"}]
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        no_dependent_fail = award | {
            "direct_or_indirect_award": {
                "is_direct": "N"
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {
            "direct_or_indirect_award": {
                "entities": [{"name": "Bob", "identifying_number": "Bob-123"}]
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_entity_fail = award | {
            "direct_or_indirect_award": {
                "is_direct": "N",
                "entities": [{"name": "Bob"}]
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_entity_fail]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_entity_empty_fail = award | {
            "direct_or_indirect_award": {
                "is_direct": "N",
                "entities": [{"name": "Bob", "identifying_number": ""}]
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_entity_empty_fail]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_passthrough_dependents(self):
        """
        If federal_award_passed_to_subrecipients is Y,
        federal_award_passed_to_subrecipients_amount must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_pass = award | {
            "subrecipients": {
                "is_passed": "Y",
                "amount": 10_000
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        no_dependent_fail = award | {
            "subrecipients": {
                "is_passed": "Y"
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {
            "subrecipients": {
                "amount": 10_000
            }
        }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_major_program_dependents(self):
        """
        If major_program is Y, major_program_audit_report_type must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_pass = award | {
            "program": {
                    "name": "Bob",
                    "number": "42.123",
                    "is_major": "Y",
                    "audit_report_type": "U",
                    "number_of_audit_findings": 0,
                    "amount_expended": 42            
                }
            }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        invalid_fail = award | {
            "program": {
                    "name": "Bob",
                    "number": "42.123",
                    "is_major": "Y",
                    "audit_report_type": "Z",
                    "number_of_audit_findings": 0,
                    "amount_expended": 42        
                }
            }
        simple_case["FederalAwards"]["federal_awards"] = [invalid_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        no_dependent_fail = award | {
                    "is_major": "Y"
            }
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award |{
                    "audit_report_type": "U",
            }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_state_cluster_name(self):
        """
        If cluster name is 'STATE CLUSTER' state_cluster_name must have a value
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)

        simple_case["FederalAwards"]["federal_awards"][0]["cluster"]["name"] = "STATE CLUSTER"
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_disallowed_state_cluster_name(self):
        """
        If cluster name is not 'STATE CLUSTER', state_cluster_name must be empty or null
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FederalAwards"]["federal_awards"][0]["cluster"]["state_cluster_name"] = "ANYTHING"
        
        # Test for errors when state_cluster_name is not empty or null
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        # Test for successful validation when state_cluster_name is empty or null
        for valid in ["", 'null']:
            simple_case = jsoncopy(self.SIMPLE_CASE)
            simple_case["FederalAwards"]["federal_awards"][0]["cluster"]["state_cluster_name"] =  valid

            validate(simple_case, schema)

    def test_number_of_audit_findings(self):
        """
        If major_program_audit_report_type is A or Q, number_of_audit_findings must be greater than 0
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FederalAwards"]["federal_awards"][0]["program"]["is_major"] = "Y"

        for report_type in ["A", "Q"]:
            # major_audit_report_type of A or Q requires non-zero number_of_audit_findings
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "audit_report_type"
            ] = report_type
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = 0
            self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = 1
            validate(simple_case, schema)

        for report_type in ["U", "D"]:
            # major_audit_report_type of U or D requires zero number_of_audit_findings
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "audit_report_type"
            ] = report_type
            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = 0
            validate(simple_case, schema)

            simple_case["FederalAwards"]["federal_awards"][0]["program"][
                "number_of_audit_findings"
            ] = 1
            self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)


class CorrectiveActionPlanSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the CorrectiveActionPlan JSON schema.
    """

    CORRECTIVE_ACTION_PLAN_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "CorrectiveActionPlan.schema.json").read_text(encoding="utf-8")
    )

    SIMPLE_CASE = {
        "CorrectiveActionPlan": {
            "auditee_ein": None,
            "corrective_action_plan_entries": [
                {
                    "contains_chart_or_table": "N",
                    "planned_action": "Action 11",
                    "reference_number": "2023-111"
                }
            ]
        }
    }

    def test_schema(self):
        """Try to test CorrectiveActionPlan first."""
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        in_flight_file = SCHEMA_DIR / CORRECTIVE_ACTION_PLAN_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest Corrective Action Plan case; none of the conditional fields
        apply.
        """
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_ein(self):
        """
        Test that validation fails if auditee_ein is missing
        """
        schema = self.CORRECTIVE_ACTION_PLAN_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["CorrectiveActionPlan"]["auditee_ein"]

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


class FindingsUniformGuidanceSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the FindingsUniformGuidance JSON schema.
    """

    FINDINGS_UNIFORM_GUIDANCE_SCHEMA = json.loads(
        (SECTION_SCHEMA_DIR / "FindingsUniformGuidance.schema.json").read_text(encoding="utf-8")
    )

    SIMPLE_CASE = {
        "FindingsUniformGuidance": {
            "auditee_ein": None,
            "findings_uniform_guidance_entries": [
                {
                    "program": {
                        "compliance_requirement": "A",
                        "name": "program name",
                        "number": "42.123"
                    },
                    "questioned_costs": "N",
                    "significiant_deficiency": "N",
                    "other_matters": "N",
                    "other_findings": "Y",
                    "modified_opinion": "N",
                    "material_weakness": "N",
                    "findings": {
                        "is_valid": "Y",
                        "repeat_prior_reference": "Y",
                        "prior_references": "2022-001",
                        "reference": "2023-001"
                    }
                }
            ]
        }
    }

    def test_schema(self):
        """Try to test FindingsUniformGuidance first."""
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        in_flight_file = SCHEMA_DIR / FINDINGS_UNIFORM_GUIDANCE_TEST_FILE
        in_flight = json.loads(in_flight_file.read_text(encoding="utf-8"))
        
        validate(in_flight, schema)

    def test_simple_pass(self):
        """
        Test the simplest FindingsUniformGuidance case; none of the conditional fields
        apply.
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        validate(self.SIMPLE_CASE, schema)

    def test_missing_auditee_ein(self):
        """
        Test that validation fails if auditee_ein is missing
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["auditee_ein"]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_entry_fields(self):
        """
        Test that validation fails if any entry field is missing
        """
        schema = self.FINDINGS_UNIFORM_GUIDANCE_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "program"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "findings"
        ]["prior_references"]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "significiant_deficiency"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "other_matters"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "other_findings"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "modified_opinion"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "material_weakness"
        ]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        simple_case = jsoncopy(self.SIMPLE_CASE)
        del simple_case["FindingsUniformGuidance"]["findings_uniform_guidance_entries"][0][
            "findings"
        ]
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
            "significiant_deficiency"
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
            "significiant_deficiency"
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