from django.conf import settings
from django.test import TestCase
from audit.models import SingleAuditChecklist, SacValidationWaiver
from census_historical_migration.invalid_record import InvalidRecord
from .check_finding_reference_uniqueness import check_finding_reference_uniqueness
from .sac_validation_shape import sac_validation_shape
from .errors import err_duplicate_finding_reference
from .utils import generate_random_integer
from model_bakery import baker


class CheckFindingReferenceUniquenessTests(TestCase):
    AWARD_MIN = 1000
    AWARD_MAX = 2000
    REF_MIN = 100
    REF_MAX = 200

    def _award_reference(self) -> str:
        return f"AWARD-{generate_random_integer(self.AWARD_MIN, self.AWARD_MAX)}"

    def _reference_number(self, ref_num=None) -> str:
        return (
            f"2023-{generate_random_integer(self.REF_MIN, self.REF_MAX)}"
            if ref_num is None
            else f"2023-{ref_num}"
        )

    def _make_findings_uniform_guidance(
        self, award_references, reference_numbers
    ) -> dict:
        entries = []
        for award_ref, ref_nums in zip(award_references, reference_numbers):
            for ref_num in ref_nums:
                entries.append(
                    {
                        "program": {"award_reference": award_ref},
                        "findings": {"reference_number": ref_num},
                    }
                )

        return {
            "FindingsUniformGuidance": {
                "auditee_uei": "ABB123456CCC",
                "findings_uniform_guidance_entries": entries,
            }
        }

    def test_no_duplicate_references(self):
        """
        Check that no error is returned when there are no duplicate reference numbers.
        """
        range_size = generate_random_integer(2, 4)
        sac = baker.make(SingleAuditChecklist)
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(
            [self._award_reference() for _ in range(range_size)],
            [[self._reference_number(self.REF_MIN + i)] for i in range(range_size)],
        )
        errors = check_finding_reference_uniqueness(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_duplicate_references_for_award(self):
        """
        Check that errors are returned for awards with duplicate reference numbers.
        """
        range_size = generate_random_integer(2, 4)
        sac = baker.make(SingleAuditChecklist)
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(
            [self._award_reference() for _ in range(range_size)],
            [
                [
                    self._reference_number(self.REF_MIN),
                    self._reference_number(self.REF_MIN),
                    self._reference_number(self.REF_MAX),
                ]
            ],
        )
        errors = check_finding_reference_uniqueness(sac_validation_shape(sac))
        for finding in sac.findings_uniform_guidance["FindingsUniformGuidance"][
            "findings_uniform_guidance_entries"
        ]:
            expected_error = {
                "error": err_duplicate_finding_reference(
                    finding["program"]["award_reference"],
                    self._reference_number(self.REF_MIN),
                )
            }
            self.assertIn(expected_error, errors)

    def test_duplicate_references_for_historical_award(self):
        """
        Check that errors are not returned for historical awards with duplicate reference numbers.
        """
        range_size = generate_random_integer(2, 4)
        sac = baker.make(SingleAuditChecklist)
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(
            [self._award_reference() for _ in range(range_size)],
            [
                [
                    self._reference_number(self.REF_MIN),
                    self._reference_number(self.REF_MIN),
                    self._reference_number(self.REF_MAX),
                ]
            ],
        )
        sac.data_source = settings.CENSUS_DATA_SOURCE
        InvalidRecord.reset()
        InvalidRecord.append_validations_to_skip("check_finding_reference_uniqueness")

        errors = check_finding_reference_uniqueness(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_duplicate_finding_reference_numbers_with_waivers(self):
        """
        Check that errors are not returned for report with duplicate reference numbers when the validation is waived.
        """
        range_size = generate_random_integer(2, 4)
        sac = baker.make(SingleAuditChecklist)
        baker.make(
            SacValidationWaiver,
            report_id=sac,
            waiver_types=[SacValidationWaiver.TYPES.FINDING_REFERENCE_NUMBER],
        )
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(
            [self._award_reference() for _ in range(range_size)],
            [
                [
                    self._reference_number(self.REF_MIN),
                    self._reference_number(self.REF_MIN),
                    self._reference_number(self.REF_MAX),
                ]
            ],
        )
        sac.waiver_types = [SacValidationWaiver.TYPES.FINDING_REFERENCE_NUMBER]
        errors = check_finding_reference_uniqueness(sac_validation_shape(sac))
        self.assertEqual(errors, [])
