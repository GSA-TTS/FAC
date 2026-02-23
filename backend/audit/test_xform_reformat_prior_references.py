from unittest.mock import Mock
from django.test import SimpleTestCase
from audit.intakelib.transforms.xform_reformat_prior_references import (
    reformat_prior_references,
)
from audit.context import set_sac_to_context

EXPECTED = [
    "2022-002",
    "2022-002,2021-001",
    "2023-003,2022-002",
    "2024-004,2023-003",
    "2025-005,2024-004,2023-003",
    "2026-006,2025-005,2024-004",
    "2022-002",
    "2023-003",
    "2027-007,2026-006,2025-005",
    "2028-008,2027-007,2026-006",
    "2029-009,2028-008,2027-007",
]


class TestFindingReferenceYear(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Form",
                "ranges": [
                    {
                        "name": "prior_references",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": [
                            "2022-002",
                            "2022-002,2021-001",
                            "2023-003, 2022-002",
                            "2024-004 ,2023-003",
                            "2025-005 , 2024-004, 2023-003",
                            "2026-006 , 2025-005 , 2024-004",
                            "2022-002 ",
                            " 2023-003",
                            "2027-007 , 2026-006 , 2025-005 ",
                            " 2028-008 , 2027-007 , 2026-006 ",
                            # Note multiline test case...
                            # noqa: W291
                            """ 2029-009 ,
                              2028-008 ,
                                2027-007
""",
                        ],
                    },
                ],
            }
        ]
        self.mock_sac = Mock()

    def test_success(self):
        """
        Test that spaces in prior reference years all get removed.
        """
        with set_sac_to_context(self.mock_sac):
            new_ir = reformat_prior_references(self.ir)
            values = new_ir[0]["ranges"][0]["values"]
            # We expect all spaces to be removed. So, each value in the
            # `values` array should match the value in the EXPECTED array.
            for expected, returned in zip(EXPECTED, values):
                self.assertEqual(expected, returned)
