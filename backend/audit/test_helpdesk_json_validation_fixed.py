import json

from django.test import TestCase
from django.contrib.auth import get_user_model

from audit.models import SingleAuditChecklist
from audit.cross_validation.validate_workbooks import run_validations

User = get_user_model()


class TestHelpdeskJSONValidationFixed(TestCase):
    """
    Helpdesk harness for confirming that corrected JSON
    produces NO pre-submission validation errors.
    """

    def test_user_errors_fixed(self):
        # ------------------------------------------------------------
        # 1. Create user (required by SAC)
        # ------------------------------------------------------------
        user = User.objects.create_user(
            username="helpdesk@example.com",
            email="helpdesk@example.com",
            password="test",
        )

        # ------------------------------------------------------------
        # 2. Corrected JSON (matches across sections)
        # ------------------------------------------------------------
        general_information = json.loads("""
        {
          "auditee_uei": "HALHR1NGUJQ8",
          "auditee_fiscal_period_start": "2023-11-01",
          "auditee_fiscal_period_end": "2024-10-31"
        }
        """)

        audit_information = json.loads("""
        {
          "agencies": ["93"]
        }
        """)

        # Federal Awards declares AWARD-00001 with 3 findings
        federal_awards = json.loads("""
        {
          "federal_awards": [
            {
              "award_reference": "AWARD-00001",
              "program": {
                "number_of_audit_findings": 3
              }
            }
          ]
        }
        """)

        # Findings now correctly reference AWARD-00001
        findings_uniform_guidance = json.loads("""
        {
          "findings_uniform_guidance_entries": [
            {
              "program": { "award_reference": "AWARD-00001" },
              "findings": { "reference_number": "2024-001" }
            },
            {
              "program": { "award_reference": "AWARD-00001" },
              "findings": { "reference_number": "2024-002" }
            },
            {
              "program": { "award_reference": "AWARD-00001" },
              "findings": { "reference_number": "2024-003" }
            }
          ]
        }
        """)

        # ------------------------------------------------------------
        # 3. Create SAC exactly like pre-submission
        # ------------------------------------------------------------
        sac = SingleAuditChecklist.objects.create(
            submitted_by=user,
            general_information=general_information,
            audit_information=audit_information,
            federal_awards=federal_awards,
            findings_uniform_guidance=findings_uniform_guidance,
        )

        # ------------------------------------------------------------
        # 4. Run validations
        # ------------------------------------------------------------
        errors = run_validations(sac)

        print("\nFIXED DATA VALIDATION:")
        for e in errors:
            print(e)

        # ------------------------------------------------------------
        # 5. There MUST be no errors
        # ------------------------------------------------------------
        self.assertEqual(errors, [])
