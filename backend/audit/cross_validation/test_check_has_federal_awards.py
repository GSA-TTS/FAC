from django.test import TestCase
from audit.models import SingleAuditChecklist
from .check_has_federal_awards import (
    check_has_federal_awards,
)
from .sac_validation_shape import sac_validation_shape
from .errors import err_no_federal_awards

from model_bakery import baker

import random


class CheckHasFederalAwardsTest(TestCase):
    def _make_federal_awards(self, num_federal_awards) -> dict:
        return {
            "FederalAwards": {
                "federal_awards": [
                    (
                        {
                            "program": {"federal_agency_prefix": "10"},
                        }
                    )
                    for _ in range(num_federal_awards)
                ],
            }
        }

    def _make_sac(self, num_federal_awards) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist)
        sac.federal_awards = self._make_federal_awards(num_federal_awards)
        return sac

    def test_zero_federal_awards(self):
        """When there are zero federal awards, we should have an error"""
        sac = self._make_sac(0)
        errors = check_has_federal_awards(sac_validation_shape(sac))
        self.assertEqual(errors, [{"error": err_no_federal_awards()}])

    def test_one_federal_award(self):
        """When there is one federal awards, we should have no errors"""
        sac = self._make_sac(1)
        errors = check_has_federal_awards(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_many_federal_awards(self):
        """When there are many federal awards, we should have no errors"""
        sac = self._make_sac(random.randint(2, 10000))
        errors = check_has_federal_awards(sac_validation_shape(sac))
        self.assertEqual(errors, [])
