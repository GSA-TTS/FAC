from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import connection

from audit.models import SingleAuditChecklist
import logging
from django.db.models import Q

# from difflib import *
from prettytable import PrettyTable
from pprint import pprint

from Levenshtein import distance

# 'difflib' is not currently part of the FAC build.

logger = logging.getLogger(__name__)

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


def edit_dist(junk, a, b):
    # This does *sequences*. That means big changes can have a
    # distance of 2.
    # seq = SequenceMatcher(isjunk=junk, a=a, b=b)
    # # Equal strings have one opcode. So, subtract one.
    # # [('equal', 0, 12, 0, 12)]
    # return len(seq.get_opcodes()) - 1
    return distance(a, b)


def prep(s):
    return s.lower()


def get_audit_year(r):
    return int(r.general_information["auditee_fiscal_period_end"].split("-")[0])


def ay_dist(r1, r2, scale=11):
    return abs(get_audit_year(r2) - get_audit_year(r1)) * scale


def uei_dist(r1, r2, scale=8):
    return (
        edit_dist(
            None,
            prep(r1.general_information["auditee_uei"]),
            prep(r2.general_information["auditee_uei"]),
        )
        * scale
    )


def ein_dist(r1, r2, scale=3):
    return (
        edit_dist(
            None,
            prep(r1.general_information["ein"]),
            prep(r2.general_information["ein"]),
        )
        * scale
    )


def auditee_email_dist(r1, r2, scale=1):
    return (
        edit_dist(
            None,
            prep(r1.general_information["auditee_email"]),
            prep(r2.general_information["auditee_email"]),
        )
        * scale
    )


def auditee_name_dist(r1, r2, scale=3):
    return (
        edit_dist(
            None,
            prep(r1.general_information["auditee_name"]),
            prep(r2.general_information["auditee_name"]),
        )
        * scale
    )


def auditee_state_dist(r1, r2, scale=8):
    s1 = r1.general_information["auditee_state"]
    s2 = r2.general_information["auditee_state"]
    return scale if s1 != s2 else 0


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


class MinDist:
    pass


def set_distance(r1, s, ndx):
    dist = 0
    for r2 in s:
        dist += audit_distance(r1, r2)
    # Do not average the distances.
    # if len(s) > 0:
    #     dist = dist / len(s)
    # print(f"{dist} {r1.report_id} <- set({ndx})")
    return dist


def order_reports_key(r):
    for ndx, tn in enumerate(list(reversed(r.transition_name))):
        if tn == "submitted":
            break
    return list(reversed(r.transition_date))[ndx]


def print_sets(AY, sets):
    with open(f"tables-{AY}-{len(sets)}.txt", "w") as table_file:
        for ndx, s in enumerate(sets):
            if len(s) > 1:
                table = PrettyTable()
                table.align = "l"
                table.field_names = ["field", "value"]

                table_file.write(f"\n===============\n")
                table_file.write(f"SET {ndx}\n")
                table_file.write(f"===============\n")

                for r in sorted(s, key=order_reports_key):
                    table.add_row(["report_id", r.report_id])
                    table.add_row(["distance", r.distance])
                    table.add_row(["order", r.order])
                    table.add_row(["audit year", get_audit_year(r)])
                    table.add_row(
                        [
                            "accepted date",
                            order_reports_key(r).strftime("%Y-%m-%d %H:%M"),
                        ]
                    )
                    table.add_row(["uei", r.general_information["auditee_uei"]])
                    table.add_row(["ein", r.general_information["ein"]])
                    table.add_row(
                        ["email", prep(r.general_information["auditee_email"])]
                    )
                    table.add_row(["name", prep(r.general_information["auditee_name"])])
                    table.add_row(
                        ["state", prep(r.general_information["auditee_state"])]
                    )
                    table.add_divider()

                table_file.write(str(table))
                table_file.write("\n\n")


import time
import csv
from django.db.models import F
from datetime import datetime


def export_sets_as_csv(AY, sets):
    with open(f"sets-{AY}-{len(sets)}.csv", "w") as csv_file:
        wr = csv.writer(csv_file)  # , quoting=csv.QUOTE_ALL
        wr.writerow(
            [
                "set_index",
                "set_distance",
                "set_order",
                "report_id",
                "audit_year",
                "fac_accepted_date",
                "auditee_uei",
                "auditee_ein",
                "auditee_email",
                "auditee_name",
                "auditee_state",
            ]
        )
        for ndx, s in enumerate(sets):
            if len(s) > 1:
                for r in sorted(s, key=order_reports_key):
                    wr.writerow(
                        [
                            ndx,
                            r.distance,
                            r.order,
                            r.report_id,
                            get_audit_year(r),
                            order_reports_key(r).strftime("%Y-%m-%d %H:%M:%S"),
                            r.general_information["auditee_uei"],
                            r.general_information["ein"],
                            prep(r.general_information["auditee_email"]),
                            prep(r.general_information["auditee_name"]),
                            prep(r.general_information["auditee_state"]),
                        ]
                    )


def generate_clusters(AY):
    print("\n-=-=-=-=-=-=-=-=-=-")
    DUPLICATION_COUNT = 2
    AUDIT_YEAR = AY

    # Begin with a small set.
    # Take a full year, grab the UEIs, and look for duplicated UEIs.
    base = SingleAuditChecklist.objects.filter(
        general_information__auditee_fiscal_period_end__startswith=AUDIT_YEAR,
        submission_status="disseminated",
    )
    print(f"{len(base)} in AY{AUDIT_YEAR}")

    ueis = (
        base.values("general_information__auditee_uei")
        .annotate(uei=F("general_information__auditee_uei"))
        .annotate(uei_duplication_count=Count("report_id"))
    ).filter(uei_duplication_count__gte=DUPLICATION_COUNT)

    print("----")
    print(f"{ueis.count()} duplicated UEIs (dupe count >= {DUPLICATION_COUNT})")
    # print(ueis[:2])

    # Now, I want the records for those UEIs
    # Order by the first date in the transition_date array.
    records = base.filter(
        general_information__auditee_uei__in=ueis.values("uei"),
    )
    # Doing it in the model is hard.
    records = sorted(
        records, key=lambda r: r.transition_date[0].strftime("%Y-%m-%d %H:%M:%S")
    )

    print("-----")
    print(f"{len(records)} records for the duplicated UEIs")
    time.sleep(3)

    # print("----")
    # print(records[:2])

    # For each record, compute its distance to the existing sets.
    # If it is below the threshold, insert it into an existing set.
    # Otherwise, insert into a new set.
    sets = []
    THRESHOLD = 3

    for rndx, r in enumerate(records):
        print(f"Processing {rndx} of {len(records)}: {r.report_id} sets: {len(sets)}")
        # Start infinitely far apart
        md = MinDist()
        md.distance = float("inf")
        md.set_index = -1

        for ndx, s in enumerate(sets):
            d = set_distance(r, s, ndx)

            if d < md.distance:
                md.distance = d
                md.set_index = ndx

        r.distance = md.distance

        if md.distance < THRESHOLD:
            # print(f"Adding {r} to {md.set_index}")
            r.order = len(sets[md.set_index])
            sets[md.set_index].add(r)
        else:
            # print(f"Adding {r} to new set ({r.__hash__()})")
            new_s = set()
            r.order = 0
            new_s.add(r)
            sets.append(new_s)

    sorted_sets = sorted(sets, key=lambda s: get_audit_year(next(iter(s))))
    print_sets(AUDIT_YEAR, sorted_sets)
    export_sets_as_csv(AUDIT_YEAR, sorted_sets)
    return sorted_sets


class Command(BaseCommand):
    """Clusters audits for resubmission linking"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--audit_year",
            type=str,
            required=True,
            help="Audit year to process",
        )

    def handle(self, *args, **options):
        generate_clusters(options["audit_year"])
