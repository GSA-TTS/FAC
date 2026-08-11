from django.test import TestCase

from audit.models import SingleAuditChecklist

from .check_auditee_auditor_ein_match import check_auditee_auditor_ein_match
from .sac_validation_shape import sac_validation_shape
from .warnings import warn_auditee_auditor_ein_match

from model_bakery import baker


class CheckAuditeeAuditorEINMatchTests(TestCase):
    def test_only_auditee_ein_present(self):
        """For a SAC with only the auditee EIN, no warning."""
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"ein": "867530900"}

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(check_auditee_auditor_ein_match(shaped_sac), [])

    def test_only_auditor_ein_present(self):
        """For a SAC with only the auditor EIN, no warning."""
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"auditor_ein": "121314151"}

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(check_auditee_auditor_ein_match(shaped_sac), [])

    def test_different_eins(self):
        """For a SAC with two different EINs, no warning."""
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"ein": "123456789", "auditor_ein": "987654321"}

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(check_auditee_auditor_ein_match(shaped_sac), [])

    def test_matching_eins_raises_warning(self):
        """For a SAC with two identical EINs, one warning with the right text."""
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"ein": "123456789", "auditor_ein": "123456789"}

        shaped_sac = sac_validation_shape(sac)

        self.assertEqual(
            check_auditee_auditor_ein_match(shaped_sac),
            [{"warning": warn_auditee_auditor_ein_match()}],
        )
