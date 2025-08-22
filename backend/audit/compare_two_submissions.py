from audit.models import SingleAuditChecklist
from copy import deepcopy
from pprint import pprint
import logging

logger = logging.getLogger(__name__)

#########################################
# The first set of functions compare dictionary-based
# fields from the SAC. This would be general_info and
# audit_info, for example.


# s1 ^ s2 is roughly (s1 - s2) U (s2 - s1) if needed.
def in_first_not_second(d1: dict, d2: dict):
    differences = []
    d1 = d1 or {}
    d2 = d2 or {}
    for k, v in d1.items():
        if k in d2:
            continue
        else:  # k not in d2:
            differences.append({"key": k, "from": v, "to": None})
    return differences


def in_second_not_first(d1: dict, d2: dict):
    differences = []
    d1 = d1 or {}
    d2 = d2 or {}
    for k, v in d2.items():
        if k in d1:
            continue
        else:  # k not in d1
            differences.append({"key": k, "from": v, "to": None})
    return differences


def in_both(d1: dict, d2: dict):
    both = []
    d1 = d1 or {}
    d2 = d2 or {}
    for k in d1.keys():
        if k in d2 and d1.get(k, None) == d2.get(k, None):
            # Unchanged; skip
            continue
        elif k in d2 and d1.get(k, None) != d2.get(k, None):
            both.append({"key": k, "from": d1[k], "to": d2[k]})
        else:
            continue
    return both


# These are dictionaries
def analyze_pair(d1, d2):
    # First, we find what is in one or the other.
    fns = in_first_not_second(d1, d2)
    snf = in_second_not_first(d1, d2)
    both = in_both(d1, d2)
    if fns == {} and snf == {} and both == {}:
        return {"status": "same"}
    return {
        "status": "changed",
        "in_r1": sorted(fns, key=lambda d: d["key"]),
        "in_r2": sorted(snf, key=lambda d: d["key"]),
        "in_both": sorted(both, key=lambda d: d["key"]),
    }


# Compare a given JSON field in the SAC object.
def compare_dictionary_fields(
    sac1: SingleAuditChecklist,
    sac2: SingleAuditChecklist,
    column: str,
):
    if getattr(sac1, column) == getattr(sac2, column):
        return {"status": "same"}
    else:
        res = analyze_pair(
            getattr_default(sac1, column, {}), getattr_default(sac2, column, {})
        )
        return res


def getattr_default(obj, key, default=None):
    try:
        res = getattr(obj, key)
        return res
    except AttributeError:
        return default


def deep_getattr(o, lok, default=None):
    oprime = deepcopy(o)
    for ndx, key in enumerate(lok):
        # print(f"{ndx+1} of {len(lok)} getting {key} in {oprime} {type(oprime)}")
        if oprime is None:
            return default
        else:
            if isinstance(oprime, dict):
                oprime = oprime.get(key, default)
            else:
                try:
                    oprime = getattr(oprime, key)
                except AttributeError:
                    oprime = default
    return oprime


def compare_lists_of_objects(
    sac1: SingleAuditChecklist, sac2: SingleAuditChecklist, keys: list, extract_fun: str
):
    # Use a list of keys to dive into an object.
    # Expect a list of objects to come back, in this case.
    # print(f"deep on {sac1}")
    ls1 = deep_getattr(sac1, keys, [])
    # print(f"deep on {sac2}")
    ls2 = deep_getattr(sac2, keys, [])

    print("COMPARING")
    pprint(ls1)
    pprint(ls2)

    # Hash the objects.
    # Key order will matter. Here's to hoping
    # our system is very consistent.
    loh1 = map(lambda o: hash(str(o)), ls1)
    loh2 = map(lambda o: hash(str(o)), ls2)

    # Build a dict map of hashes to objects
    map1 = {}
    for h, o in zip(loh1, ls1):
        map1[h] = o
    map2 = {}
    for h, o in zip(loh2, ls2):
        map2[h] = o

    print("MAP 1")
    pprint(map1)
    print("MAP 2")
    pprint(map2)

    # If the maps are identical, we can just return now.
    if map1 == map2:
        return {"status": "same"}

    # The keys can be sets
    ks1 = set(map1.keys())
    ks2 = set(map2.keys())

    # Keys only in ks1
    only_in_1 = ks1 - ks2
    # Keys only in ks2
    only_in_2 = ks2 - ks1

    res = {"status": "changed", "in_r1": list(), "in_r2": list(), "in_both": list()}

    for k in only_in_1:
        res["in_r1"].append(extract_fun(map1[k]))
    for k in only_in_2:
        res["in_r2"].append(extract_fun(map2[k]))

    # Finally, to find everything "in both", we'll take all of the keys from both,
    # map them through the extract_fun, turn it into a set, and call it done.
    # Take the intersection.
    res["in_both"] = set(map(extract_fun, map1.values())) & set(
        map(extract_fun, map2.values())
    )

    return res


def report_id_to_sac(rid):
    if isinstance(rid, str):
        return SingleAuditChecklist.objects.get(report_id=rid)
    elif isinstance(rid, SingleAuditChecklist):
        return rid
    else:
        logger.error(f"{rid} is not a report_id string")
        return None


def are_two_sacs_identical(sac1, sac2):
    fields = [
        "submission_status",
        "data_source",
        # "transition_name",
        # "transition_date",
        "report_id",
        "audit_type",
        "general_information",
        "audit_information",
        "federal_awards",
        "corrective_action_plan",
        "findings_text",
        "findings_uniform_guidance",
        "additional_ueis",
        "additional_eins",
        "secondary_auditors",
        "notes_to_sefa",
        "tribal_data_consent",
        "cognizant_agency",
        "oversight_agency",
    ]
    they_are_the_same = True
    for field in fields:
        if getattr_default(sac1, field, None) != getattr_default(sac2, field, None):
            they_are_the_same = False
            break
    return they_are_the_same


# We want to take two report IDs, and return something that looks like
#
# {
#    "general": { "status": "same" }
#    "federal_awards": {
#       "status": "changed",
#       "r1_minus_r2": [...], # What is in (or changed in) r1 that is not in r2?
#       "r2_minus_r1": [...]  # What is in (or changed in) r2 that is not in r1?
# }
#
# Consider using deepdiff
# https://miguendes.me/the-best-way-to-compare-two-dictionaries-in-python
# This walks a JSON tree and finds the differences, and nicely spells them out.
def compare_report_ids(rid_1, rid_2):
    sac_r1 = report_id_to_sac(rid_1)
    sac_r2 = report_id_to_sac(rid_2)
    if sac_r1 is None or sac_r2 is None:
        logger.error(
            f"compare_report_ids expects two report ID strings or two SAC objects, given {sac_r1} and {sac_r2}"
        )
        return {"status": "error"}

    # Do an early check, and bail if the same.
    if are_two_sacs_identical(sac_r1, sac_r2):
        return {"status": "identical"}

    summary = {}
    ###############
    # general_information
    res = compare_dictionary_fields(sac_r1, sac_r2, "general_information")
    summary["general_information"] = res

    ###############
    # audit_information
    res = compare_dictionary_fields(sac_r1, sac_r2, "audit_information")
    summary["audit_information"] = res

    ###############
    # all the forms that have lists of things.
    accessors = [
        [
            ["federal_awards", "FederalAwards", "federal_awards"],
            lambda entry: entry["award_reference"],
        ],
        [
            [
                "corrective_action_plan",
                "CorrectiveActionPlan",
                "corrective_action_plan_entries",
            ],
            lambda entry: entry["reference_number"],
        ],
        [
            [
                "findings_text",
                "FindingsText",
                "findings_text_entries",
            ],
            lambda entry: entry["reference_number"],
        ],
        [
            [
                "findings_uniform_guidance",
                "FindingsUniformGuidance",
                "findings_uniform_guidance_entries",
            ],
            lambda entry: entry["program"]["award_reference"]
            + "/"
            + entry["findings"]["reference_number"],
        ],
        [
            [
                "additional_ueis",
                "AdditionalUeis",
                "additional_ueis_entries",
            ],
            lambda entry: entry["additional_uei"],
        ],
        [
            [
                "additional_eins",
                "AdditionalEINs",
                "additional_eins_entries",
            ],
            lambda entry: entry["additional_ein"],
        ],
        [
            [
                "secondary_auditors",
                "SecondaryAuditors",
                "secondary_auditors_entries",
            ],
            lambda entry: entry["secondary_auditor_name"],
        ],
        [
            [
                "notes_to_sefa",
                "NotesToSefa",
                "notes_to_sefa_entries",
            ],
            lambda entry: str(entry["seq_number"]) + ": " + entry["note_title"],
        ],
    ]

    for ls in accessors:
        logger.info(f"{ls[0][0]}")
        res = compare_lists_of_objects(sac_r1, sac_r2, ls[0], ls[1])
        summary[ls[0][0]] = res

    ###############
    # tribal_data_consent
    res = compare_dictionary_fields(sac_r1, sac_r2, "tribal_data_consent")
    summary["tribal_data_consent"] = res

    return summary


def compare_with_prev(rid):
    if isinstance(rid, str):
        sac = SingleAuditChecklist.objects.get(report_id=rid)
    elif isinstance(rid, SingleAuditChecklist):
        sac = rid
    else:
        logger.error(f"{rid} is not a report ID or SAC object")
        return {"status": "error"}

    if sac.resubmission_meta:
        if "previous_report_id" in sac.resubmission_meta:
            prev = sac.resubmission_meta["previous_report_id"]
        elif "next_report_id" in sac.resubmission_meta:
            prev = sac.report_id
            rid = sac.resubmission_meta["next_report_id"]
        else:
            logger.error(f"No previous report ID for {rid}")
            return {"status": "error", "message": f"no previous report for {rid}"}
        logger.info(f"COMPARING PREV {prev} WITH NEXT {rid}")
        return compare_report_ids(prev, rid)

    return {"status": "error", "message": "No resubmission_meta in sac."}


# The summary comes back as:
# {
#     "general_information": {
#         "status": "changed",
#         "in_r1": {"ein": "370906335"},
#         "in_r2": {"ein": "123456789"},
#     },
#     "audit_information": {"status": "same"},
#     "federal_awards": {
#         "status": "changed",
#         "in_r1": ["AWARD-0003"],
#         "in_r2": ["AWARD-0003"],
#     },
#     "corrective_action_plan": {"status": "same"},
#     "findings_text": {"status": "same"},
#     "findings_uniform_guidance": {
#         "status": "changed",
#         "in_r1": ["AWARD-0009/2022-001"],
#         "in_r2": [],
#     },
#     "additional_ueis": {"status": "same"},
#     "additional_eins": {"status": "same"},
#     "secondary_auditors": {"status": "same"},
#     "notes_to_sefa": {"status": "same"},
#     "tribal_data_consent": {"status": "same"},
# }


# Columns we could compare.
# A *** means we are currently comparing it.
# columns = [
#     # "submission_status",
#     # "data_source",
#     # "transition_name",
#     # "transition_date",
#     # "report_id",
#     # "audit_type",
#     # "general_information", ***
#     # "audit_information", ***
#     # "federal_awards", ***
#     # "corrective_action_plan", ***
#     # "findings_text", ***
#     # "findings_uniform_guidance", ***
#     # "additional_ueis", ***
#     # "additional_eins", ***
#     # "secondary_auditors", ***
#     # "notes_to_sefa", ***
#     # "tribal_data_consent", ***
#     # "cognizant_agency",
#     # "oversight_agency",
# ]
