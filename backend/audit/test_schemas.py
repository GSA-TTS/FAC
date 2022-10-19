# Even though the schemas are not Django views or modules etc., we test them
# here for CI/CD integration.
import json
from pathlib import Path
from django.test import SimpleTestCase
from jsonschema import exceptions, validate

# Simplest way to create a new copy of simple case rather than getting
# references to things used by other tests:
jsoncopy = lambda v: json.loads(json.dumps(v))

SCHEMA_DIR = Path(__file__).parent.parent / "schemas" / "sections"


class SchemaValidityTest(SimpleTestCase):
    """
    Test the basic validiy of the JSON schemas.
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
            "direct_award_pass_through_entities": [
                {
                    "name": "Bob",
                }
            ],
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
