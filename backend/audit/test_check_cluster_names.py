import json
from unittest.mock import mock_open, patch
from django.test import SimpleTestCase

from .intakelib.checks.check_cluster_names import check_cluster_names


class TestCheckForGsaMigrationKeyword(SimpleTestCase):
    def setUp(self):
        self.ir_with_invalid_cluster_names = [
            {
                "name": "Sheet1",
                "ranges": [
                    {
                        "name": "cluster_name",
                        "start_cell": {"column": "A", "row": "1"},
                        "end_cell": {"column": "A", "row": "3"},
                        "values": [
                            "InvalidCluster1",
                            "ValidCluster",
                            "InvalidCluster2",
                        ],
                    }
                ],
            }
        ]

        self.ir_with_valid_cluster_names = [
            {
                "name": "Sheet1",
                "ranges": [
                    {
                        "name": "cluster_name",
                        "start_cell": {"column": "A", "row": "1"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["ValidCluster1", "ValidCluster2"],
                    }
                ],
            }
        ]

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            {"cluster_names": ["ValidCluster1", "ValidCluster2", "ValidCluster"]}
        ),
    )
    @patch("json.load", side_effect=lambda file: json.loads(file.read()))
    def test_with_invalid_cluster_names(self, mock_json_load, mock_open):
        errors = check_cluster_names(self.ir_with_invalid_cluster_names)
        expected_error_count = 2  # As there are 2 invalid cluster names

        self.assertEqual(
            len(errors),
            expected_error_count,
            "Number of errors does not match the expected count",
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            {"cluster_names": ["ValidCluster1", "ValidCluster2", "ValidCluster"]}
        ),
    )
    @patch("json.load", side_effect=lambda file: json.loads(file.read()))
    def test_with_valid_cluster_names(self, mock_json_load, mock_open):
        errors = check_cluster_names(self.ir_with_valid_cluster_names)
        self.assertEqual(
            len(errors), 0, "There should be no errors for valid cluster names"
        )
