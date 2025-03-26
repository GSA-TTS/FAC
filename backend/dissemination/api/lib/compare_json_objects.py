import random


def andmap(ls) -> bool:
    result = True
    for v in ls:
        result = result and v
    return result


def check_dictionaries_have_same_keys(o1, o2):
    key_set_1 = set(o1.keys())
    key_set_2 = set(o2.keys())
    return key_set_1 == key_set_2


def check_dictionaries_have_same_values(o1, o2):
    val_set_1 = set(o1.values())
    val_set_2 = set(o2.values())
    return val_set_1 == val_set_2


def check_dictionaries_have_same_mappings(o1, o2):
    for k in o1.keys():
        if o1[k] == o2[k]:
            pass
        else:
            return False
    return True


def compare_json_objects(o1: dict, o2: dict) -> bool:
    # We want to confirm that these two objects are identical.
    # o1 must have the same keys as o2
    # o1 must have the same values as o2
    # the mapping from [k1, v1] must be the same for [k2, v2]

    # Check if the keys for both objects are the same
    if not check_dictionaries_have_same_keys(o1, o2):
        print("object keys are not equal")
        return False

    if not check_dictionaries_have_same_values(o1, o2):
        print("object values are not equal")
        return False

    # At this point, we have the same keys and the same
    # values in each object. Now, we have to make sure
    # that the keys in o1 and o2 map to identical values.
    if not check_dictionaries_have_same_mappings(o1, o2):
        print(f"mappings not identical in objects")
        return False

    # If we made it this far, we think they are the same.
    return True


def compare_any_order(l1: list, l2: list, comparison_key: str = "report_id") -> list:
    results = []
    for o1 in l1:
        to_compare = None

        # We're taking one object (o1) and
        # looking through the second result set to find the same object based on
        # the key (by default) `report_id`. This way, we can then compare one object
        # to another, and be certain we're comparing the same thing.
        # We *should* be able to guarantee order.
        for o2 in l2:
            if comparison_key in o2 and o1[comparison_key] == o2[comparison_key]:
                # print(f"Comparing against 1 {o2}")
                to_compare = o2
                break

        # If we can't find an object to compare to, we might
        # as well record a false and break now.
        # print(f"Comparing against 2 {to_compare}")
        if not to_compare:
            print(f"No object found for comparison")
            results.append(False)
            break
        elif o1[comparison_key] == to_compare[comparison_key]:
            results.append(compare_json_objects(o1, to_compare))
        else:
            print(f"Values do not match for key {comparison_key}")
            results.append(False)
            break
    return results


def compare_strict_order(l1: list, l2: list) -> list:
    results = []
    for o1, o2 in zip(l1, l2):
        results.append(compare_json_objects(o1, o2))
    return results


def check_lists_same_length(l1, l2):
    return len(l1) == len(l2)


KEY_IN_BOTH = 0
KEY_MISSING_L1 = 1
KEY_MISSING_L2 = 2


def check_key_in_both_lists(l1, l2, comparison_key):
    # Is the key in every object of l1?
    if not andmap(map(lambda o: comparison_key in o, l1)):
        return KEY_MISSING_L1
    if not andmap(map(lambda o: comparison_key in o, l2)):
        return KEY_MISSING_L2
    return KEY_IN_BOTH


def check_equal_values_for_key(l1, l2, comparison_key):
    kv1 = set(map(lambda o: o[comparison_key], l1))
    kv2 = set(map(lambda o: o[comparison_key], l2))
    return kv1 == kv2


# Compares two lists of JSON objects
# Uses the key to find which objects should be compared
def compare_lists_of_json_objects(
    l1: list, l2: list, comparison_key: str = "report_id", strict_order=True
) -> bool:

    # The lists must be the same length
    if not check_lists_same_length(l1, l2):
        print(f"len(l1) <- {len(l1)}, len(l2) <- {len(l2)}")
        return False

    # Make sure all objects in both lists all have they key
    key_in_lists = check_key_in_both_lists(l1, l2, comparison_key)
    if key_in_lists == KEY_IN_BOTH:
        pass
    elif key_in_lists == KEY_MISSING_L1:
        print(f"key {comparison_key} missing in l1")
        return False
    elif key_in_lists == KEY_MISSING_L2:
        print(f"key {comparison_key} missing in l2")
        return False
    else:
        print("impossible key check condition found; should never be here.")
        return False

    # The set of values in l1 for this key must be the same as the set of
    # values in l2 for this key.
    if not check_equal_values_for_key(l1, l2, comparison_key):
        print(f"Values not equal in all objects for {comparison_key}")

    if strict_order:
        results = compare_strict_order(l1, l2)
    else:
        results = compare_any_order(l1, l2)

    # We don't have an andmap(). We want to return
    # True if everything in the list is True.
    and_mapped = True
    for r in results:
        and_mapped = and_mapped and r
    # print(f"andmap: {and_mapped}")
    return and_mapped
