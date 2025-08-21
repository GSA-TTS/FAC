from audit.models import SingleAuditChecklist
from copy import deepcopy
from pprint import pprint
import logging

logger = logging.getLogger(__name__)


# s1 ^ s2 is roughly (s1 - s2) U (s2 - s1) if needed.
def in_first_not_second(d1: dict, d2: dict):
    differences = []
    for k, v in d1.items():
        if k in d2 and d1[k] == d2[k]:
            continue
        elif k in d2 and d1[k] != d2[k]:
            differences.append({k: v})
        else:  # k not in d2:
            differences.append({k: v})
    return differences


def in_second_not_first(d1: dict, d2: dict):
    differences = []
    for k, v in d2.items():
        if k in d1 and d2[k] == d1[k]:
            continue
        elif k in d1 and d2[k] != d1[k]:
            differences.append({k: v})
        else:  # k not in d1
            differences.append({k: v})
    return differences


# The `in_*_not_*` functions return sets; we want dictionaries.
# def set_tuples_to_dict(st):
#     # Given a set containing tuples, convert it to a dict.
#     res = {}
#     for o in st:
#         res[o[0]] = o[1]
#     return res


def getattr_default(obj, key, default=None):
    res = getattr(obj, key)
    if res:
        return res
    else:
        return default


def deep_getattr(o, lok, default=None):
    oprime = deepcopy(o)
    for ndx, key in enumerate(lok):
        # print(f"{ndx+1} of {len(lok)} getting {key} in {oprime} {type(oprime)}")
        if oprime is None:
            return default
        else:
            if isinstance(oprime, dict):
                oprime = oprime[key]
            else:
                oprime = getattr(oprime, key)
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

    # If the hashes are all the same, nothing changed.
    if map1 == map2:
        return {"status": "same"}
    else:
        res = {
            "status": "changed",
            "in_r1": list(),
            "in_r2": list(),
        }
        # For each hash in the first map, if it is in the second map,
        # skip it. That means the values are the same.
        for h1, o1 in map1.items():
            if h1 in map2:
                continue
            else:
                # If they're different, then we'll put that into the
                # first map. That means it is present in the first submission,
                # but not the second.
                res["in_r1"].append(extract_fun(o1))
        # For each in the second, do a reverse check.
        for h2, o2 in map2.items():
            # If it is in both, skip.
            if h2 in map1:
                continue
            else:
                # If it is different in R2, keep it. We may end up
                # with the same object in both (because it is present in both,
                # but the object changed in some way), which we'll handle in a sec.
                res["in_r2"].append(extract_fun(o2))

    # Sort things.
    res["in_r1"] = sorted(res["in_r1"])
    res["in_r2"] = sorted(res["in_r2"])

    return res


# Compare a given JSON field in the SAC object.
def compare_dictionary_fields(
    sac1: SingleAuditChecklist,
    sac2: SingleAuditChecklist,
    column: str,
):
    if getattr(sac1, column) == getattr(sac2, column):
        return {"status": "same"}
    else:
        return {
            "status": "changed",
            "in_r1": in_first_not_second(
                getattr_default(sac1, column, {}), getattr_default(sac2, column, {})
            ),
            "in_r2": in_second_not_first(
                getattr_default(sac1, column, {}), getattr_default(sac2, column, {})
            ),
        }


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
    if isinstance(rid_1, str) and isinstance(rid_2, str):
        sac_r1 = SingleAuditChecklist.objects.get(report_id=rid_1)
        sac_r2 = SingleAuditChecklist.objects.get(report_id=rid_2)
    elif isinstance(rid_1, SingleAuditChecklist) and isinstance(
        rid_2, SingleAuditChecklist
    ):
        sac_r1 = rid_1
        sac_r2 = rid_2
    else:
        print("ERROR DANGER WILL ROBINSON")

    summary = {}
    ###############
    # general_information
    logger.info("general_information")
    res = compare_dictionary_fields(sac_r1, sac_r2, "general_information")
    summary["general_information"] = res

    ###############
    # audit_information
    logger.info("audit_information")
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
                "AdditionalEins",
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
