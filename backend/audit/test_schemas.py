# Even though the schemas are not Django views or modules etc., we test them
# here for CI/CD integration.
import json
from pathlib import Path
from django.test import SimpleTestCase
from jsonschema import exceptions, validate

# Simplest way to create a new copy of simple case rather than getting
# references to things used by other tests:
jsoncopy = lambda v: json.loads(json.dumps(v))

SCHEMA_DIR = Path(__file__).parent.parent.parent / "schemas" / "sections"


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
                    "federal_agency_prefix": "a",
                    "cfda_three_digit_extension": "zxcv",
                    "federal_program_name": "GACC",
                    "amount_expended": "",
                    "cluster_name": "",
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
