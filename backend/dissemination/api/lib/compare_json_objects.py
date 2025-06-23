# flake8: noqa

# To make understanding differences easier, all the functions will return
# objects instead of booleans.
from typing import Any

import re


class APIValue:
    def __init__(self, version, key, value, report_id):
        self.version = version
        self.key = key
        self.value = value
        self.report_id = report_id

    def __str__(self):
        return f"<{self.version}, {self.key}, {self.value}, {self.report_id}>"


class ErrorPair:
    def __init__(self, type, e1, e2):
        self.type = type
        self.e1 = e1
        self.e2 = e2

    def __str__(self):
        return f"[{self.type}, {self.e1}, {self.e2}]"


class Result:
    def __init__(self, b, error_pair=None):
        self.bool = b
        self.errors = []
        if error_pair:
            self.errors.append(error_pair)

    def add_error(self, error_pair):
        self.errors.append(error_pair)

    def set_result(self, b):
        self.bool = b

    def get_errors(self):
        return self.errors

    def __bool__(self):
        return self.bool

    def __str__(self):
        return "\n".join([str(ep) for ep in self.errors])


def andmap(ls):
    result = True
    for v in ls:
        result = result and v
    return Result(result)


def check_dictionaries_have_same_keys(v1, o1, v2, o2):
    key_set_1 = set(o1.keys())
    key_set_2 = set(o2.keys())
    result = key_set_1 == key_set_2
    R = Result(result)
    if not result:
        for k in key_set_1:
            if k not in key_set_2:
                R.add_error(
                    ErrorPair(
                        "dict_keys",
                        APIValue(v1, k, k, o1["report_id"]),
                        APIValue(v2, k, None, o2["report_id"]),
                    )
                )
        for k in key_set_2:
            if k not in key_set_1:
                R.add_error(
                    ErrorPair(
                        "dict_keys",
                        APIValue(v1, k, None, o1["report_id"]),
                        APIValue(v2, k, k, o2["report_id"]),
                    )
                )
    return R


def check_dictionaries_have_same_values(v1, o1, v2, o2, ignore={}):
    # Remove the ignores from the objects
    for k in ignore.keys():
        # print(f"popping {k} before {len(o1)}")
        o1.pop(k, None)
        # print(f"popping {k} after {len(o1)}")
        o2.pop(k, None)

    val_set_1 = set([safely_remove_spaces(o) for o in o1.values()])
    val_set_2 = set([safely_remove_spaces(o) for o in o2.values()])

    result = val_set_1 == val_set_2

    R = Result(result)

    if not result:
        for v in val_set_1:
            if v not in val_set_2:
                # R.add_error("mismatched value", f"'{v}' not in object 2")
                R.add_error(
                    ErrorPair(
                        "dict_values",
                        APIValue(v1, k, v, o1["report_id"]),
                        APIValue(v2, k, None, o2["report_id"]),
                    )
                )
        for v in val_set_2:
            if v not in val_set_1:
                # R.add_error("mismatched value", f"'{v}' not in object 1")
                R.add_error(
                    ErrorPair(
                        "dict_values",
                        APIValue(v1, k, None, o1["report_id"]),
                        APIValue(v2, k, v, o2["report_id"]),
                    )
                )
    return R


def skippable(k, obj, ignore):
    if k in ignore:
        for rule_k, rule_vs in ignore[k]["acceptable_values"].items():
            for rule in rule_vs:
                if re.search(rule, obj[rule_k]):
                    # print("found", rule, obj[rule_k])
                    return True
    return False


def safely_remove_spaces(o):
    if isinstance(o, str):
        return o.replace(" ", "")
    else:
        return o


def check_not_equal(o1, o2):
    return safely_remove_spaces(o1) != safely_remove_spaces(o2)


def check_dictionaries_have_same_mappings(v1, o1, v2, o2, ignore={}):
    R = Result(True)
    for k in o1.keys():
        # Skip values that we say to ignore
        if (
            k in ignore
            and (
                re.search(ignore[k]["api_version"], v1)
                or re.search(ignore[k]["api_version"], v2)
            )
            and (skippable(k, o1, ignore) or skippable(k, o2, ignore))
        ):
            continue

        if k not in o2:
            R.add_error(
                ErrorPair(
                    "mappings_missing_o2",
                    APIValue(v1, k, o1[k], o1["report_id"]),
                    APIValue(v2, k, None, o2["report_id"]),
                )
            )
            R.set_result(False)

        if check_not_equal(o1[k], o2[k]):
            # print("check_not_equal", k, anded, k_in_ignore, ignorable_api, is_skippable)
            R.add_error(
                ErrorPair(
                    "mappings_not_equal",
                    APIValue(v1, k, o1[k], o1["report_id"]),
                    APIValue(v2, k, o2[k], o2["report_id"]),
                )
            )
            R.set_result(False)

    # Loop through o2 keys that may not be in o1
    for k in o2.keys():
        # Skip values we say to ignore
        if (
            k in ignore
            and re.search(ignore[k]["api_version"], v2)
            and skippable(k, o2, ignore)
        ):
            # print(f"skipping {k} - {o2['report_id']} in {v2}")
            continue

        if k not in o1:
            R.add_error(
                ErrorPair(
                    "mappings_missing_o1",
                    APIValue(v1, k, None, o1["report_id"]),
                    APIValue(v2, k, o2[k], o2["report_id"]),
                )
            )
            R.set_result(False)

    return R


def compare_json_objects(v1: str, o1: dict, v2: str, o2: dict, ignore={}):
    # We want to confirm that these two objects are identical.
    # o1 must have the same keys as o2
    # o1 must have the same values as o2
    # the mapping from [k1, v1] must be the same for [k2, v2]

    # At this point, we have the same keys and the same
    # values in each object. Now, we have to make sure
    # that the keys in o1 and o2 map to identical values.
    cdhsm = check_dictionaries_have_same_mappings(v1, o1, v2, o2, ignore=ignore)
    if not cdhsm:
        # print(f"mappings not identical in objects")
        return cdhsm

    # Check if the keys for both objects are the same
    cdhsk = check_dictionaries_have_same_keys(v1, o1, v2, o2)
    if not cdhsk:
        return cdhsk

    cdhsv = check_dictionaries_have_same_values(v1, o1, v2, o2, ignore=ignore)
    if not cdhsv:
        return cdhsv

    # If we made it this far, we think they are the same.
    return Result(True)


def compare_any_order(
    v1: str,
    l1: list,
    v2: str,
    l2: list,
    comparison_key: str = "report_id",
    ignore={},
):
    results = []

    # print(f"cao {len(l1)} {len(l2)} {v1} {v2} {comparison_key}")

    for o1 in l1:
        to_compare = None

        # We're taking one object (o1) and
        # looking through the second result set to find the same object based on
        # the key (by default) `report_id`. This way, we can then compare one object
        # to another, and be certain we're comparing the same thing.
        # We *should* be able to guarantee order.
        for o2 in l2:
            if comparison_key in o2 and o1[comparison_key] == o2[comparison_key]:
                to_compare = o2
                break

        # If we can't find an object to compare to, we might
        # as well record a false and break now.
        if not to_compare:

            # print(f"No object found for comparison")
            results.append(
                # Result(False, "empty comparison", "no object found to compare against")
                Result(
                    False,
                    ErrorPair(
                        "comparison_obj_not_found",
                        APIValue(
                            v1, comparison_key, o1[comparison_key], o1["report_id"]
                        ),
                        APIValue(
                            v2, comparison_key, o2[comparison_key], o2["report_id"]
                        ),
                    ),
                )
            )
            # 20240623 MCJ should this be continue or break?
            continue
        elif o1[comparison_key] == to_compare[comparison_key]:
            results.append(compare_json_objects(v1, o1, v2, to_compare, ignore=ignore))
        else:
            print(f"Values do not match for key {comparison_key}")
            results.append(
                Result(
                    False,
                    ErrorPair(
                        "comparison_key_not_matched",
                        APIValue(
                            v1, comparison_key, o1[comparison_key], o1["report_id"]
                        ),
                        APIValue(
                            v2,
                            comparison_key,
                            to_compare[comparison_key],
                            o2["report_id"],
                        ),
                    ),
                )
            )
            continue
    return results


def compare_strict_order(v1: str, l1: list, v2: str, l2: list, ignore={}):
    results = []
    for o1, o2 in zip(l1, l2):
        results.append(compare_json_objects(v1, o1, v2, o2, ignore=ignore))
    return results


def check_lists_same_length(v1, l1, v2, l2):
    result = len(l1) == len(l2)
    R = None
    if result:
        R = Result(True)
    else:
        R = Result(
            False,
            ErrorPair(
                "list_length",
                APIValue(v1, "list_length", len(l1), None),
                APIValue(v2, "list_length", len(l2), None),
            ),
        )

    report_ids_1 = [o["report_id"] for o in l1]
    report_ids_2 = [o["report_id"] for o in l2]

    for rid in report_ids_1:
        if rid not in report_ids_2:
            # print(rid, "not in l2")
            R.add_error(
                ErrorPair(
                    "missing_in_l2",
                    APIValue(v1, "report_id", rid, None),
                    APIValue(v2, "report_id", None, None),
                )
            )
    for rid in report_ids_2:
        if rid not in report_ids_1:
            # print(rid, "not in l1")
            R.add_error(
                ErrorPair(
                    "missing_in_l1",
                    APIValue(v1, "report_id", None, None),
                    APIValue(v2, "report_id", rid, None),
                )
            )
    return R


KEY_IN_BOTH = 0
KEY_MISSING_L1 = 1
KEY_MISSING_L2 = 2


def check_key_in_both_lists(v1, l1, v2, l2, comparison_key):
    # Is the key in every object of l1?
    if not andmap(map(lambda o: comparison_key in o, l1)):
        return KEY_MISSING_L1
    if not andmap(map(lambda o: comparison_key in o, l2)):
        return KEY_MISSING_L2
    return KEY_IN_BOTH


def check_equal_values_for_key(v1, l1, v2, l2, comparison_key, ignore={}):

    kv1 = set(map(lambda o: o[comparison_key], l1))
    kv2 = set(map(lambda o: o[comparison_key], l2))

    # FIXME: Right here, we should look for a rule in `ignore` that uses
    # this key. For example, `auditor_certify_name` could appear here.
    # Then, we should do the right thing with the values---like check/ignore.
    # Although... as used, this might *always* be "report_id."

    result = kv1 == kv2
    R = Result(result)
    if not result:
        # R.add_error(f"{comparison_key} returned different values", f"{kv1 - kv2}")
        R.add_error(
            ErrorPair(
                "eq_val_for_key",
                APIValue(v1, comparison_key, kv1 - kv2, None),
                APIValue(v2, comparison_key, kv2 - kv1, None),
            )
        )
    return R


def remove_objects_from_lists(l1, l2, ignore):
    # Get the report IDs we might skip because they are
    # stuck. Pull from the dictionary.
    if ignore:
        ignore_stuck_report_ids = ignore["stuck_reports"]["report_ids"]
    else:
        ignore_stuck_report_ids = []

    # Filter out stuck audits
    newl1 = []
    newl2 = []
    for obj in l1:
        if obj["report_id"] in ignore_stuck_report_ids:
            pass
        else:
            newl1.append(obj)
    for obj in l2:
        if obj["report_id"] in ignore_stuck_report_ids:
            pass
        else:
            newl2.append(obj)

    return newl1, newl2


# Compares two lists of JSON objects
# Uses the key to find which objects should be compared
def compare_lists_of_json_objects(
    v1: str,
    l1: list,
    v2: str,
    l2: list,
    comparison_key: str = "report_id",
    strict_order=True,
    ignore={},
):

    # Lets remove all of the report IDs from both lists that should be
    # skipped. These are, currently, a list of stuck reports on the
    # v1.1 side. They will not have comparisons in the SOT table.
    l1, l2 = remove_objects_from_lists(l1, l2, ignore)

    # The lists must be the same length
    clsl = check_lists_same_length(v1, l1, v2, l2)
    print(f"Objects from {v1}: {len(l1)}")
    print(f"Objects from {v2}: {len(l2)}")

    if not clsl:
        # print(f"lists different lenths: l1 <- {len(l1)} l2 <- {len(l2)}")
        return [clsl]

    # Make sure all objects in both lists all have they key
    key_in_lists = check_key_in_both_lists(v1, l1, v2, l2, comparison_key)
    if key_in_lists == KEY_IN_BOTH:
        pass
    elif key_in_lists == KEY_MISSING_L1:
        return [
            Result(
                False,
                ErrorPair(
                    "check_in_both_lists",
                    APIValue(v1, comparison_key, None, None),
                    APIValue(v2, comparison_key, True, None),
                ),
            )
        ]
    elif key_in_lists == KEY_MISSING_L2:
        return [
            Result(
                False,
                ErrorPair(
                    "missing_comparison_key",
                    APIValue(v1, comparison_key, None, None),
                    APIValue(v2, comparison_key, True, None),
                ),
            )
        ]
    else:
        # print("impossible key check condition found; should never be here.")
        return [
            Result(
                False,
                ErrorPair(
                    "impossible; should never be here",
                    APIValue(v1, comparison_key, None, None),
                    APIValue(v2, comparison_key, None, None),
                ),
            )
        ]

    # The set of values in l1 for this key must be the same as the set of
    # values in l2 for this key.
    set_eq = check_equal_values_for_key(v1, l1, v2, l2, comparison_key, ignore=ignore)
    if not set_eq:
        print(f"Values not equal in all objects for {comparison_key}")
        return [set_eq]

    if strict_order:
        results = compare_strict_order(v1, l1, v2, l2, ignore=ignore)
    else:
        results = compare_any_order(v1, l1, v2, l2, ignore=ignore)

    # We don't have an andmap(). We want to return
    # True if everything in the list is True.
    and_mapped = True
    for r in results:
        and_mapped = and_mapped and r
    if and_mapped:
        return Result(True)
    else:
        return results
