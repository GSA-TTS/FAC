from django.test import TestCase
from model_bakery import baker
from audit.models import SingleAuditChecklist
from config.settings import DOLLAR_THRESHOLD

from .errors import err_total_amount_expended
from .check_total_amount_expended import check_total_amount_expended
from .sac_validation_shape import sac_validation_shape


class CheckTotalAmountExpendedTests(TestCase):
    """
    Tests for check_total_amount_expended
    """

    def _make_federal_awards(self, total_amount_expended) -> dict:
        return {"FederalAwards": {"total_amount_expended": total_amount_expended}}

    def test_total_amount_expended_equal_threshold(self):
        """
        total_amount_expended at the threshold should pass.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.federal_awards = self._make_federal_awards(DOLLAR_THRESHOLD)

        validation_result = check_total_amount_expended(sac_validation_shape(sac))

        self.assertEqual(validation_result, [])

    def test_total_amount_expended_above_threshold(self):
        """
        total_amount_expended above the threshold should pass.
        """
        sac = baker.make(SingleAuditChecklist)
        total_amount_expended = DOLLAR_THRESHOLD + 1
        sac.federal_awards = self._make_federal_awards(total_amount_expended)

        validation_result = check_total_amount_expended(sac_validation_shape(sac))

        self.assertEqual(validation_result, [])

    def test_total_amount_expended_below_threshold(self):
        """
        total_amount_expended below the threshold should fail.
        """
        sac = baker.make(SingleAuditChecklist)
        total_amount_expended = DOLLAR_THRESHOLD - 1
        sac.federal_awards = self._make_federal_awards(total_amount_expended)

        validation_result = check_total_amount_expended(sac_validation_shape(sac))

        self.assertEqual(len(validation_result), 1)
        self.assertEqual(
            validation_result[0],
            {"error": err_total_amount_expended(total_amount_expended)},
        )
