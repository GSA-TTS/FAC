from django.test import TestCase

from audit.models import SingleAuditChecklist

from .check_name_fields_not_unique import check_name_fields_not_unique
from .sac_validation_shape import sac_validation_shape
from .warnings import warn_name_fields_not_unique

from model_bakery import baker


class CheckNameFieldsNotUniqueTests(TestCase):
    def test_all_fields_absent(self):
        """For a SAC with no name fields, no warning."""
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"auditee_uei": "ABCDEFGH1234"}

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(check_name_fields_not_unique(shaped_sac), [])

    def test_one_field_present_no_duplicate(self):
        """For a SAC with only one name field, no warning."""
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"auditee_name": "Super Cool Company"}

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(check_name_fields_not_unique(shaped_sac), [])

    def test_all_fields_unique(self):
        """For a SAC with fully distinct name fields, no warning."""
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "auditee_name": "Super Cool Public Entity",
            "auditee_contact_name": "James the Auditee",
            "auditor_contact_name": "James the Auditor",
            "auditor_firm_name": "Super Cool Auditing Firm",
        }

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(check_name_fields_not_unique(shaped_sac), [])

    def test_two_fields_match_raises_one_warning(self):
        """For a SAC with two identical name fields, one warning."""
        same_name = "Oops All Auditees"

        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "auditee_name": same_name,
            "auditor_firm_name": same_name,
        }

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(
            check_name_fields_not_unique(shaped_sac),
            [
                {
                    "warning": warn_name_fields_not_unique(
                        ["Auditee Name", "Auditor Firm Name"], same_name
                    )
                }
            ],
        )

    def test_three_fields_match_raises_one_warning(self):
        """For a SAC with three identical name fields, one warning."""
        same_name = "Oops All Auditees"
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "auditee_name": same_name,
            "auditee_contact_name": same_name,
            "auditor_firm_name": same_name,
        }

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(
            check_name_fields_not_unique(shaped_sac),
            [
                {
                    "warning": warn_name_fields_not_unique(
                        ["Auditee Name", "Auditee Contact Name", "Auditor Firm Name"],
                        same_name,
                    )
                }
            ],
        )

    def test_two_independent_duplicate_sets_raises_two_warnings(self):
        """For a SAC with two pairs of identical name fields, two warnings."""
        same_auditee_name = "Oops All Auditees"
        same_auditor_name = "Oops All Auditors"
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "auditee_name": same_auditee_name,
            "auditee_contact_name": same_auditee_name,
            "auditor_firm_name": same_auditor_name,
            "auditor_contact_name": same_auditor_name,
        }

        shaped_sac = sac_validation_shape(sac)

        result = check_name_fields_not_unique(shaped_sac)

        self.assertEqual(len(result), 2)
        self.assertIn(
            {
                "warning": warn_name_fields_not_unique(
                    ["Auditee Name", "Auditee Contact Name"], same_auditee_name
                )
            },
            result,
        )
        self.assertIn(
            {
                "warning": warn_name_fields_not_unique(
                    ["Auditor Contact Name", "Auditor Firm Name"], same_auditor_name
                )
            },
            result,
        )
