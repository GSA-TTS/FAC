from compare_json_objects import compare_json_objects as cjo
from compare_json_objects import compare_lists_of_json_objects as clojo
from api_support import compare

import os


def test_small_equal1():
    o1 = {"a": 1}
    o2 = {"a": 1}
    assert cjo(o1, o2) == True


def test_small_equal2():
    # Key order should not matter
    o1 = {"a": 1, "b": 2}
    o2 = {"b": 2, "a": 1}
    assert cjo(o1, o2) == True


def test_small_unequal1():
    o1 = {"a": 1}
    o2 = {"a": 2}
    assert cjo(o1, o2) == False


def test_small_unequal2():
    o1 = {"a": 1, "b": 2}
    o2 = {"a": 1}
    assert cjo(o1, o2) == False


def test_small_unequal3():
    o1 = {"a": 1, "b": 2}
    o2 = {"a": 1, "b": 3}
    assert cjo(o1, o2) == False


def test_small_unequal3():
    o1 = {"a": 1, "b": 2}
    o2 = {"a": 2, "b": 1}
    assert cjo(o1, o2) == False


def test_lod_equal1():
    l1 = [{"report_id": 1}]
    l2 = [{"report_id": 1}]
    assert clojo(l1, l2, comparison_key="report_id")


def test_lod_equal2():
    l1 = [{"report_id": 1}, {"report_id": 2}]
    l2 = [{"report_id": 2}, {"report_id": 1}]
    # report_id is the default key
    # With strict ordering, these are different
    assert clojo(l1, l2, strict_order=True) == False
    # If we allow the order to shuffle, they are the same.
    assert clojo(l1, l2, strict_order=False) == True


def test_lod_not_equal1():
    l1 = [{"report_id": 1}]
    l2 = [{"report_id": 1}, {"something_else": 2}]
    assert clojo(l1, l2, comparison_key="report_id") == False


def test_lod_not_equal2():
    l1 = [{"report_id": 1}, {"report_id": 3}]
    l2 = [{"report_id": 1}, {"report_id": 2}]
    assert clojo(l1, l2, comparison_key="report_id") == False


def test_lod_not_equal3():
    l1 = [{"report_id": 1}, {"not_something": 2}]
    l2 = [{"report_id": 1}, {"something_else": 2}]
    assert clojo(l1, l2, comparison_key="something_else") == False


def test_live1():
    if os.getenv("FAC_API_USER_ID"):
        compare(
            "http",
            "localhost",
            "localhost",
            "api_v1_1_0",
            "api_v1_1_0",
            "general",
            3000,
            report_id=None,
            start_date="2023-03-01",
            end_date="2023-03-03",
            environment="local",
            comparison_key="report_id",
            strict_order=True,
        )
