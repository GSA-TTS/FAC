# Even though the schemas are not Django views or modules etc., we test them
# here for CI/CD integration.
import json
import string

from pathlib import Path
from django.test import SimpleTestCase
from jsonschema import exceptions, validate as jsonschema_validate, FormatChecker
from random import choice, randrange

# Simplest way to create a new copy of simple case rather than getting
# references to things used by other tests:
jsoncopy = lambda v: json.loads(json.dumps(v))


# wrap the validate function to include a format checker
def validate(instance, schema):
    return jsonschema_validate(instance, schema, format_checker=FormatChecker())


SCHEMA_DIR = Path(__file__).parent.parent / "schemas" / "sections"


class GeneralInformationSchemaValidityTest(SimpleTestCase):
    """
    Test the basic validity of the GeneralInformation JSON schema.
    """

    GENERAL_INFO_SCHEMA = json.loads(
        (SCHEMA_DIR / "GeneralInformation.schema.json").read_text(encoding="utf-8")
    )

    SIMPLE_CASE = {
        "GeneralInformation": {
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
        simple_case["GeneralInformation"]["auditee_fiscal_period_start"] = bad_date

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
        simple_case["GeneralInformation"]["auditee_fiscal_period_end"] = bad_date

        self.assertRaisesRegex(
            exceptions.ValidationError,
            f"'{bad_date}' is not a 'date'",
            validate,
            simple_case,
            schema,
        )

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

                instance["GeneralInformation"]["ein"] = bad_ein

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

                instance["GeneralInformation"]["auditee_uei"] = bad_uei

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

        instance["GeneralInformation"]["auditee_uei"] = good_uei

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

                    instance["GeneralInformation"][zip_field] = bad_zip

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

                    instance["GeneralInformation"][zip_field] = bad_zip

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

                    instance["GeneralInformation"][phone_field] = good_phone

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

                    instance["GeneralInformation"][phone_field] = bad_phone

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
        (SCHEMA_DIR / "FederalAwards.schema.json").read_text(encoding="utf-8")
    )

    SIMPLE_CASE = {
        "FederalAwards": {
            "auditee_ein": "whatever",
            "total_amount_expended": "",
            "federal_awards": [
                {
                    "program_number": "10.001",
                    "federal_program_name": "GACC",
                    "amount_expended": "",
                    "cluster_name": "N/A",
                    "loan_or_loan_guarantee": "N",
                    "direct_award": "Y",
                    "federal_award_passed_to_subrecipients": "N",
                    "major_program": "N",
                    "number_of_audit_findings": 0,
                }
            ],
        }
    }

    def test_schema(self):
        """Try to test FederalAwards first."""
        schema = self.FEDERAL_AWARDS_SCHEMA
        in_flight_file = SCHEMA_DIR / "sample-federal-awards.json"
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
        If loan_or_loan_guarantee is Y, loan_balance_at_audit_period_end must
        have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_int_pass = award | {
            "loan_or_loan_guarantee": "Y",
            "loan_balance_at_audit_period_end": 10_000,
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_int_pass]

        validate(simple_case, schema)

        both_na_pass = award | {
            "loan_or_loan_guarantee": "Y",
            "loan_balance_at_audit_period_end": "N/A",
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_na_pass]

        validate(simple_case, schema)

        no_dependent_fail = award | {"loan_or_loan_guarantee": "Y"}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {"loan_balance_at_audit_period_end": 10_000}
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_value_fail = award | {
            "loan_or_loan_guarantee": "Y",
            "loan_balance_at_audit_period_end": "",
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_value_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        zero_value_fail = award | {
            "loan_or_loan_guarantee": "Y",
            "loan_balance_at_audit_period_end": 0,
        }
        simple_case["FederalAwards"]["federal_awards"] = [zero_value_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_direct_award_dependents(self):
        """
        If direct_award is Y, loan_balance_at_audit_period_end must
        have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_pass = award | {
            "direct_award": "N",
            "direct_award_pass_through_entities": [
                {"name": "Bob", "identifying_number": "Bob-123"}
            ],
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        no_dependent_fail = award | {"direct_award": "N"}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {"direct_award_pass_through_entities": 10_000}
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_entity_fail = award | {
            "direct_award": "N",
            "direct_award_pass_through_entities": [{"name": "Bob"}],
        }
        simple_case["FederalAwards"]["federal_awards"] = [bad_entity_fail]
        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        bad_entity_empty_fail = award | {
            "direct_award": "N",
            "direct_award_pass_through_entities": [
                {"name": "Bob", "identifying_number": ""}
            ],
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
            "federal_award_passed_to_subrecipients": "Y",
            "federal_award_passed_to_subrecipients_amount": 10_000,
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        no_dependent_fail = award | {"federal_award_passed_to_subrecipients": "Y"}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {
            "federal_award_passed_to_subrecipients_amount": 10_000
        }
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_major_program_dependents(self):
        """
        If major_program is Y,
        major_program_audit_report_type must have a value.
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        award = jsoncopy(simple_case["FederalAwards"]["federal_awards"][0])

        both_pass = award | {
            "major_program": "Y",
            "major_program_audit_report_type": "U",
        }
        simple_case["FederalAwards"]["federal_awards"] = [both_pass]

        validate(simple_case, schema)

        invalid_fail = award | {
            "major_program": "Y",
            "major_program_audit_report_type": "Z",
        }
        simple_case["FederalAwards"]["federal_awards"] = [invalid_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        no_dependent_fail = award | {"major_program": "Y"}
        simple_case["FederalAwards"]["federal_awards"] = [no_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        only_dependent_fail = award | {"major_program_audit_report_type": "U"}
        simple_case["FederalAwards"]["federal_awards"] = [only_dependent_fail]

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_missing_state_cluster_name(self):
        """
        If cluster_name is 'State Cluster'
        state_cluster must have a value
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FederalAwards"]["federal_awards"][0][
            "cluster_name"
        ] = "STATE CLUSTER"

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

    def test_disallowed_state_cluster_name(self):
        """
        If cluster_name is not 'State Cluster'
        state_cluster_name must not be present
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FederalAwards"]["federal_awards"][0][
            "state_cluster_name"
        ] = "Not blank"

        self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

        # blank should be permissible
        simple_case["FederalAwards"]["federal_awards"][0]["state_cluster_name"] = ""
        validate(simple_case, schema)

        # missing should be permissible
        del simple_case["FederalAwards"]["federal_awards"][0]["state_cluster_name"]
        validate(simple_case, schema)

    def test_number_of_audit_findings(self):
        """
        If major_program_audit_report_type is A or Q,
        number_of_audit_findings must be greater than 0
        """
        schema = self.FEDERAL_AWARDS_SCHEMA

        simple_case = jsoncopy(self.SIMPLE_CASE)
        simple_case["FederalAwards"]["federal_awards"][0]["major_program"] = "Y"

        for report_type in ["A", "Q"]:
            # major_audit_report_type of A or Q requires non-zero number_of_audit_findings
            simple_case["FederalAwards"]["federal_awards"][0][
                "major_program_audit_report_type"
            ] = report_type
            simple_case["FederalAwards"]["federal_awards"][0][
                "number_of_audit_findings"
            ] = 0
            self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)

            simple_case["FederalAwards"]["federal_awards"][0][
                "number_of_audit_findings"
            ] = 1
            validate(simple_case, schema)

        for report_type in ["U", "D"]:
            # major_audit_report_type of U or D requires zero number_of_audit_findings
            simple_case["FederalAwards"]["federal_awards"][0][
                "major_program_audit_report_type"
            ] = report_type
            simple_case["FederalAwards"]["federal_awards"][0][
                "number_of_audit_findings"
            ] = 0
            validate(simple_case, schema)

            simple_case["FederalAwards"]["federal_awards"][0][
                "number_of_audit_findings"
            ] = 1
            self.assertRaises(exceptions.ValidationError, validate, simple_case, schema)
