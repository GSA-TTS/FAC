"""
This is a dynamic programming solution to a complex problem.

https://github.com/GSA-TTS/FAC/issues/5102

Previous audits that were "resubmitted" want to be linked using our
new metadata. However, many people misuse UEIs and EINs.

This is a clustering algorithm designed to build the linkages
between previously "resubmitted" audits. It uses a novel
distance function to calculate the "distance" between two SF-SAC
records and cluster them for linking based on the similarity between
those records.
"""

from Levenshtein import distance


def edit_dist(junk, a, b):
    # This does *sequences*. That means big changes can have a
    # distance of 2.
    # seq = SequenceMatcher(isjunk=junk, a=a, b=b)
    # # Equal strings have one opcode. So, subtract one.
    # # [('equal', 0, 12, 0, 12)]
    # return len(seq.get_opcodes()) - 1
    return distance(a, b)


# prep_string :: string -> string
# Returns a string ready for comparison
def prep_string(s):
    return s.lower()


# get_audit_year :: Record -> integer year
# Extracts the year from a record (e.g. SingleAuditchecklist, FakeSAC)
# and returns an integer representation of the audit year
def get_audit_year(r):
    return int(r.general_information["auditee_fiscal_period_end"].split("-")[0])


# ay_dist :: record, record, scaling factor -> integer
# calculates the scaled distance between the audit year in two records
def ay_dist(r1, r2, scale=11):
    return abs(get_audit_year(r2) - get_audit_year(r1)) * scale


# uei_dist :: record, record, scaling factor -> integer
# calculates the scaled distance between two UEIs in two records
def uei_dist(r1, r2, scale=8):
    return (
        edit_dist(
            None,
            prep_string(r1.general_information["auditee_uei"]),
            prep_string(r2.general_information["auditee_uei"]),
        )
        * scale
    )


# ein_dist :: record, record, scaling factor -> integer
def ein_dist(r1, r2, scale=3):
    return (
        edit_dist(
            None,
            prep_string(r1.general_information["ein"]),
            prep_string(r2.general_information["ein"]),
        )
        * scale
    )


# auditee_email_dist :: record, record, scaling factor -> integer
def auditee_email_dist(r1, r2, scale=1):
    return (
        edit_dist(
            None,
            prep_string(r1.general_information["auditee_email"]),
            prep_string(r2.general_information["auditee_email"]),
        )
        * scale
    )


# auditee_name_dist :: record, record, scaling factor -> integer
def auditee_name_dist(r1, r2, scale=3):
    return (
        edit_dist(
            None,
            prep_string(r1.general_information["auditee_name"]),
            prep_string(r2.general_information["auditee_name"]),
        )
        * scale
    )


# auditee_state_dist :: record, record, scaling factor -> integer
def auditee_state_dist(r1, r2, scale=8):
    s1 = r1.general_information["auditee_state"]
    s2 = r2.general_information["auditee_state"]
    return scale if s1 != s2 else 0


# audit_distance :: record, record -> integer
# calcualtes the distance between two audit records
def audit_distance(r1, r2):
    # Calculate the distance
    d = 0
    for dist_fun in [
        ay_dist,
        uei_dist,
        ein_dist,
        auditee_email_dist,
        auditee_name_dist,
        auditee_state_dist,
    ]:
        # print("\t", dist_fun, dist_fun(r1, r2))
        d = d + dist_fun(r1, r2)
    return d


# set_distance :: record, set-of records -> integer
# sum of distances between a record and each record in a set
def set_distance(r1, s):
    dist = 0
    for r2 in s:
        dist += audit_distance(r1, r2)
    return dist
