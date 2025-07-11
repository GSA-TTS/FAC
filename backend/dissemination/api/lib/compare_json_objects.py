# flake8: noqa

# To make understanding differences easier, all the functions will return
# objects instead of booleans.
from typing import Any

import re
import time


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

    def __add__(self, other):
        newR = Result(self.bool and other.bool)
        for e in self.get_errors() + other.get_errors():
            newR.add_error(e)
        return newR


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
    # ASSUME IGNORABLES ARE ALREADY FILTERED OUT

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
                        APIValue(v1, "-", v, o1["report_id"]),
                        APIValue(v2, "-", None, o2["report_id"]),
                    )
                )
        for v in val_set_2:
            if v not in val_set_1:
                # R.add_error("mismatched value", f"'{v}' not in object 1")
                R.add_error(
                    ErrorPair(
                        "dict_values",
                        APIValue(v1, "-", None, o1["report_id"]),
                        APIValue(v2, "-", v, o2["report_id"]),
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
    # ASSUME IGNORABLES ARE ALREADY FILTERED OUT

    # We already checked that they have the same keys.
    # This means we can just go through one object once for comparison.
    R = Result(True)

    for k in o1.keys():
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
    return R


def compare_json_objects(v1: str, o1: dict, v2: str, o2: dict, ignore={}):
    # We want to confirm that these two objects are identical.
    # o1 must have the same keys as o2
    # o1 must have the same values as o2
    # the mapping from [k1, v1] must be the same for [k2, v2]

    # Check if the keys for both objects are the same
    # This is faster to check first. Then we don't have to check again.
    # As {k: v} dictionaries, this makes sure all `k` are the same
    # in both objects via set comparisons.
    cdhsk = check_dictionaries_have_same_keys(v1, o1, v2, o2)
    if not cdhsk:
        return cdhsk

    # Filter out what we're going to ignore up front.
    for k_ig in ignore:
        # For each ignorable key
        if (
            (k_ig in o1 or k_ig in o2)
            and (
                re.search(ignore[k_ig]["api_version"], v1)
                or re.search(ignore[k_ig]["api_version"], v2)
            )
            and (skippable(k_ig, o1, ignore) or skippable(k_ig, o2, ignore))
        ):
            o1.pop(k_ig, None)
            o2.pop(k_ig, None)

    # Now that we know we have the same keys, we should check to see
    # if we have the same values mapped to the keys.
    # Or, for each (k1, k2) in {k1: v1} and {k2: v2}, are v1 == v2?
    # This is a fast check. If it fails, do a more detailed check.
    cdhsv = check_dictionaries_have_same_values(v1, o1, v2, o2, ignore=ignore)
    if not cdhsv:
        cdhsm = check_dictionaries_have_same_mappings(v1, o1, v2, o2, ignore=ignore)
        if not cdhsm:
            # Both values will be Result objects, which we can add together into a single
            # new Result object. We can just return cdhsm, because it will re-do (in more detail)
            # the work of cdhsv
            return cdhsm

    # If we made it this far, we think they are the same.
    return Result(True)


dicts_are_preloaded = False


def compare_any_order(
    v1: str,
    l1: list,
    v2: str,
    l2: list,
    comparison_key: str = "report_id",
    ignore={},
):
    global dicts_are_preloaded
    l1_lookup = dict()
    l2_lookup = dict()

    timing_window = {}
    num_batches = 10
    batch_no = 0
    timing_window_size = len(l1) // num_batches or 1
    timing_index = 1
    total_time = 0.0

    results = list()

    # Preload some dictionaries. We were doing a nested loop over l1 and l2, which
    # was very expensive. This makes it an O(1) lookup on report_id in the lookup tables.
    # FIXME: Need to think about what this looks for tables that are not `general`
    if not dicts_are_preloaded:
        dicts_are_preloaded = True

        for o in l1:
            l1_lookup[o[comparison_key]] = o
        for o in l2:
            l2_lookup[o[comparison_key]] = o

    for o1 in l1_lookup.values():
        t0 = time.time()

        # Assuming the lookup key is "report_id"...
        # This will get the L2 object with that report ID.
        to_compare = l2_lookup.get(o1[comparison_key], None)

        # If we can't find an object to compare to, we might
        # as well record a false and break now.
        if to_compare == None:
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
                            v2,
                            comparison_key,
                            to_compare[comparison_key],
                            to_compare["report_id"],
                        ),
                    ),
                )
            )
        elif to_compare:  # o1[comparison_key] == to_compare[comparison_key]:
            compare_result = compare_json_objects(v1, o1, v2, to_compare, ignore=ignore)
            t1 = time.time()
            delta = t1 - t0
            total_time += delta
            timing_window[timing_index] = delta
            timing_index = (timing_index + 1) % timing_window_size
            if timing_index == 0:
                sum = 0.0
                for v in timing_window.values():
                    sum += v
                batch_no += 1
                # This print at least gives us something to look forward to while running.
                print(
                    f"average time per comparison ({timing_window_size*batch_no} of {len(l1)}): {(sum/timing_window_size):0.6f}"
                )
            if not compare_result:
                results.append(compare_result)
        else:
            # print(f"Values do not match for key {comparison_key}")
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
                            to_compare["report_id"],
                        ),
                    ),
                )
            )

    print(f"Time to compare_any_order: {total_time:0.2f}")
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
            R.add_error(
                ErrorPair(
                    "missing_in_l2",
                    APIValue(v1, "report_id", rid, None),
                    APIValue(v2, "report_id", None, None),
                )
            )
    for rid in report_ids_2:
        if rid not in report_ids_1:
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
        return [clsl]

    # Make sure all objects in both lists all have they key
    t0 = time.time()
    key_in_lists = check_key_in_both_lists(v1, l1, v2, l2, comparison_key)
    t1 = time.time()
    print(f"key in both lists check: {(t1-t0):0.4f}s")

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
    t0 = time.time()
    set_eq = check_equal_values_for_key(v1, l1, v2, l2, comparison_key, ignore=ignore)
    t1 = time.time()
    print(f"equal values for key time: {(t1-t0):0.4f}s")

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


def compare_sefa(
    v1: str,
    l1: list,
    v2: str,
    l2: list,
    ignore={},
):
    results = []
    l1, l2 = remove_objects_from_lists(l1, l2, ignore)
    v1_by_rid = v_by_rid(l1)
    v2_by_rid = v_by_rid(l2)
    all_rids = set(list(v1_by_rid.keys()) + list(v2_by_rid.keys()))

    for rid in all_rids:
        if rid not in v1_by_rid:
            results.append(
                Result(
                    False,
                    ErrorPair(
                        "missing_comparison_key",
                        APIValue(v1, "report_id", None, None),
                        APIValue(v2, "report_id", rid, rid),
                    ),
                )
            )
        elif rid not in v2_by_rid:
            results.append(
                Result(
                    False,
                    ErrorPair(
                        "missing_comparison_key",
                        APIValue(v1, "report_id", rid, rid),
                        APIValue(v2, "report_id", None, None),
                    ),
                )
            )
        else:
            v1_notes = v1_by_rid[rid]
            v2_notes = v2_by_rid[rid]
            v1_notes_len = len(v1_notes)
            v2_notes_len = len(v2_notes)

            if v1_notes_len != v2_notes_len:
                results.append(
                    Result(
                        False,
                        ErrorPair(
                            "len_notes_mismatch",
                            APIValue(v1, "report_id", v1_notes_len, rid),
                            APIValue(v2, "report_id", v2_notes_len, rid),
                        ),
                    )
                )
            else:
                for v1_note in v1_notes:
                    match_found = False
                    for v2_note in v2_notes:
                        if v1_note == v2_note:
                            match_found = True
                            break
                    if not match_found:
                        results.append(
                            Result(
                                False,
                                ErrorPair(
                                    "note_not_found",
                                    APIValue(v1, "report_id", v1_note, rid),
                                    APIValue(v2, "report_id", None, rid),
                                ),
                            )
                        )

                for v2_note in v2_notes:
                    match_found = False
                    for v1_note in v1_notes:
                        if v2_note == v1_note:
                            match_found = True
                            break
                    if not match_found:
                        results.append(
                            Result(
                                False,
                                ErrorPair(
                                    "note_not_found",
                                    APIValue(v1, "report_id", None, rid),
                                    APIValue(v2, "report_id", v2_note, rid),
                                ),
                            )
                        )

    return results or Result(True)


def v_by_rid(l):
    v_by_rid = {}

    for o in l:
        rid = o["report_id"]
        if rid in v_by_rid:
            v_by_rid[rid].append(o)
        else:
            v_by_rid[rid] = [o]

    return v_by_rid
