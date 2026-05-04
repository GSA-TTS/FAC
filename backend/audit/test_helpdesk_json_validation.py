from django.test import TestCase

from audit.cross_validation.check_award_ref_declaration import (
    check_award_ref_declaration,
)
from audit.cross_validation.check_findings_count_consistency import (
    check_findings_count_consistency,
)


class TestHelpdeskJSONValidation(TestCase):
    def test_user_errors(self):
        """
        This test reproduces the exact user-facing
        pre-submission validation errors using JSON only.
        """

        sac_dict = {
            "sf_sac_sections": {
                "federal_awards": {
                    "federal_awards": [
                        {
                            "award_reference": "AWARD-00001",
                            "program": {
                                "number_of_audit_findings": 3,
                            },
                        },
                        {
                            "award_reference": "AWARD-00002",
                            "program": {
                                "number_of_audit_findings": 0,
                            },
                        },
                    ]
                },
                "findings_uniform_guidance": {
                    "findings_uniform_guidance_entries": [
                        {
                            "program": {
                                "award_reference": "AWARD-93224",
                            },
                            "findings": {
                                "reference_number": "2024-001",
                            },
                        },
                        {
                            "program": {
                                "award_reference": "AWARD-93224",
                            },
                            "findings": {
                                "reference_number": "2024-002",
                            },
                        },
                        {
                            "program": {
                                "award_reference": "AWARD-93224",
                            },
                            "findings": {
                                "reference_number": "2024-003",
                            },
                        },
                    ]
                },
            }
        }

        award_ref_errors = check_award_ref_declaration(sac_dict)
        findings_count_errors = check_findings_count_consistency(sac_dict)

        print("\nAWARD REF ERRORS:")
        for e in award_ref_errors:
            print(e)

        print("\nFINDINGS COUNT ERRORS:")
        for e in findings_count_errors:
            print(e)

        # These MUST fail for this user
        self.assertTrue(award_ref_errors)
        self.assertTrue(findings_count_errors)
