from django.test import TestCase
from audit.models import Audit
from .audit_validation_shape import audit_validation_shape
from .check_has_federal_awards import (
    check_has_federal_awards,
)
from .errors import err_no_federal_awards

from model_bakery import baker

import random


class CheckHasFederalAwardsTest(TestCase):
    def _make_federal_awards(self, num_federal_awards) -> dict:
        return {
            "federal_awards": {
                "awards": [
                    (
                        {
                            "program": {"federal_agency_prefix": "10"},
                        }
                    )
                    for _ in range(num_federal_awards)
                ],
            }
        }

    def _make_audit(self, num_federal_awards) -> Audit:
        return baker.make(
            Audit, version=0, audit={**self._make_federal_awards(num_federal_awards)}
        )

    def test_zero_federal_awards(self):
        """When there are zero federal awards, we should have an error"""
        audit = self._make_audit(0)
        errors = check_has_federal_awards(audit_validation_shape(audit))
        self.assertEqual(errors, [{"error": err_no_federal_awards()}])

    def test_one_federal_award(self):
        """When there is one federal awards, we should have no errors"""
        audit = self._make_audit(1)
        errors = check_has_federal_awards(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def test_many_federal_awards(self):
        """When there are many federal awards, we should have no errors"""
        audit = self._make_audit(random.randint(2, 10000))
        errors = check_has_federal_awards(audit_validation_shape(audit))
        self.assertEqual(errors, [])
