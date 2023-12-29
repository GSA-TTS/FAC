import json
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .intakelib.transforms.xform_federal_awards_cluster_name_to_uppercase import (
    convert_federal_awards_cluster_name_to_uppercase,
)


class TestFederalAwardsClusterNameToUppercase(SimpleTestCase):
    """
    Given an intermediate representation, make the values of the cluster_name range
    uppercase.
    """

    ir_with_lowercase_cluster_names = [
        {
            "name": "Sheet1",
            "ranges": [
                {
                    "name": "cluster_name",
                    "start_cell": {"column": "A", "row": "1"},
                    "end_cell": {"column": "A", "row": "2"},
                    "values": ["ValidCluster1", "ValidCluster2", "ValidCluster"],
                }
            ],
        }
    ]

    def test_with_valid_cluster_names(self):
        """
        Test that the valid cluster names are converted.
        """
        result = convert_federal_awards_cluster_name_to_uppercase(
            self.ir_with_lowercase_cluster_names
        )
        transformed_values = result[0]["ranges"][0]["values"]
        expected_values = ["VALIDCLUSTER1", "VALIDCLUSTER2", "VALIDCLUSTER"]
        self.assertEqual(expected_values, transformed_values)

    def test_with_invalid_cluster_names(self):
        """
        Test that non-string cluster names raise errors.
        """
        ir_copy = json.loads(json.dumps(self.ir_with_lowercase_cluster_names))
        ir_copy[0]["ranges"][0]["values"] = [None, 11, True]

        with self.assertRaises(ValidationError):
            convert_federal_awards_cluster_name_to_uppercase(ir_copy)

        # In order to access the error, we seem to also have to do this:
        try:
            convert_federal_awards_cluster_name_to_uppercase(ir_copy)
        except ValidationError as err:
            self.assertEqual(3, len(err.error_list))
            self.assertIn("Invalid cluster name", str(err))
