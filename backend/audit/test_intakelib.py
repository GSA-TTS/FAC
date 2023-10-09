from django.test import SimpleTestCase
from copy import deepcopy
from audit.intakelib.intermediate_representation import (
    ranges_to_rows,
    remove_null_rows
)

class IRTests(SimpleTestCase):
    s1 = {
        "ranges": [
        {
            "values": [1, 2, 3, None, None],
        },
        {
            "values": ["a", "b", "c", None, None],
        },
        {
            "values": [8, None, 10, None, None],
        }
        ]
    }

    s2 = {
        "ranges": [
        {
            "values": [1, None, None, None, None],
        },
        {
            "values": ["a", "b", "c", None, None],
        },
        {
            "values": [8, None, 10, None, None],
        }

        ]
    }

    r1 = {
        "ranges": [
        {
            "values": [1, 2, 3],
        },
        {
            "values": ["a", "b", "c"],
        },
        {
            "values": [8, None, 10],
        }
        ]
    }

    r2 = {
        "ranges": [
        {
            "values": [1, None, None],
        },
        {
            "values": ["a", "b", "c"],
        },
        {
            "values": [8, None, 10],
        }

        ]
    }

    def test_ranges_to_rows(self):

        self.assertEqual(
            [[1, 'a', 8], [2, 'b', None], [3, 'c', 10]],
            ranges_to_rows(IRTests.s1["ranges"])
            )

        self.assertEqual(
            [[1, 'a', 8], [None, 'b', None], [None, 'c', 10]],
            ranges_to_rows(IRTests.s2["ranges"])
            )


    def test_remove_null_rows(self):
        cp = deepcopy(IRTests.s1)
        remove_null_rows(cp)
        self.assertEqual(cp, IRTests.r1)

        cp = deepcopy(IRTests.s2)
        remove_null_rows(cp)
        self.assertEqual(cp, IRTests.r2)
