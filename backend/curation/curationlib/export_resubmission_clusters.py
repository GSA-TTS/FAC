# from prettytable import PrettyTable
from curation.curationlib.audit_distance import prep_string, get_audit_year
import csv

# All of the code in here is fiddly, and output-type
# code for inspection/analysis post-facto.

NEWLINE = "\n"


def order_reports_key(r):
    for ndx, tn in enumerate(list(reversed(r.transition_name))):
        if tn == "submitted":
            break
    return list(reversed(r.transition_date))[ndx]


# Exports data as plain text tables for human inspection
# For example:
#     ===============
#     SET 0
#     ===============
#     +---------------+---------------------------+
#     | field         | value                     |
#     +---------------+---------------------------+
#     | report_id     | 2022-03-CENSUS-0000085490 |
#     | distance      | inf                       |
#     | order         | 0                         |
#     | audit year    | 2022                      |
#     | accepted date | 2022-10-06 00:00          |
#     | uei           | RSPGAXJK4555              |
#     | ein           | 581394645                 |
#     | email         | email@fac.gsa.gov         |
#     | name          | medlink georgia, inc.     |
#     | state         | ga                        |
#     +---------------+---------------------------+
#     | report_id     | 2022-03-GSAFAC-0000372569 |
#     | distance      | 0                         |
#     | order         | 1                         |
#     | audit year    | 2022                      |
#     | accepted date | 2025-06-20 00:00          |
#     | uei           | RSPGAXJK4555              |
#     | ein           | 581394645                 |
#     | email         | email@fac.gsa.gov         |
#     | name          | medlink georgia, inc.     |
#     | state         | ga                        |
#     +---------------+---------------------------+


# def export_sets_as_text_tables(AY, sets, noisy=False):
#     with open(f"{AY}-resubmission-sets-{len(sets)}.txt", "w") as table_file:
#         for ndx, s in enumerate(sets):
#             if len(s) > 1:
#                 table = PrettyTable()
#                 table.align = "l"
#                 table.field_names = ["field", "value"]

#                 table_file.write(f"\n===============\n")
#                 table_file.write(f"SET {ndx}\n")
#                 table_file.write(f"===============\n")

#                 for r in sorted(s, key=order_reports_key):
#                     table.add_row(["report_id", r.report_id])
#                     table.add_row(["distance", r.distance])
#                     table.add_row(["order", r.order])
#                     table.add_row(["audit year", get_audit_year(r)])
#                     table.add_row(
#                         [
#                             "accepted date",
#                             order_reports_key(r).strftime("%Y-%m-%d %H:%M"),
#                         ]
#                     )
#                     table.add_row(["uei", r.general_information["auditee_uei"]])
#                     table.add_row(["ein", r.general_information["ein"]])
#                     table.add_row(
#                         ["email", prep_string(r.general_information["auditee_email"])]
#                     )
#                     table.add_row(
#                         ["name", prep_string(r.general_information["auditee_name"])]
#                     )
#                     table.add_row(
#                         ["state", prep_string(r.general_information["auditee_state"])]
#                     )
#                     table.add_divider()

#                 table_file.write(str(table))
#                 table_file.write("\n\n")


# Exports the same data in CSV format for analysis in a spreadsheet tool.
def export_sets_as_csv(AY, sets, noisy=False):
    with open(f"{AY}-resubmission-sets-{len(sets)}.csv", "w") as csv_file:
        wr = csv.writer(csv_file)
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
                            prep_string(r.general_information["auditee_email"]),
                            prep_string(r.general_information["auditee_name"]),
                            prep_string(r.general_information["auditee_state"]),
                        ]
                    )


def write_row(s, md, row_tag, key_fun):
    md.write(f"| {row_tag} ")

    for ndx, r in enumerate(sorted(s, key=order_reports_key)):
        # Printing data is annoying.
        FIRST = ndx == 0
        LAST = ndx == len(s) - 1

        md.write("| ")
        md.write(key_fun(r))

        if LAST and not FIRST:
            md.write(" |")
    md.write(NEWLINE)


# Exports the set data as Markdown for use on the WWW.
def export_sets_as_markdown(AY, sets, noisy=False):
    with open(f"{AY}-resubmission-sets-{len(sets)}.md", "w") as md:

        md.write(f"### Resubmissions for audit year {AY}" + NEWLINE + NEWLINE)

        for ndx, s in enumerate(sets):
            if len(s) > 1:
                md.write(
                    f"#### UEI {s[0].general_information['auditee_uei']}" + NEWLINE
                )
                for ndx, _ in enumerate(s):
                    if ndx in [0, 1]:
                        md.write("| ")
                    else:
                        md.write("| ... <small>resubmitted as</small> ")
                # We write a tag, and close. Hence extra pipes.
                md.write(" | ... <small>resubmitted as</small> |" + NEWLINE)

                for ndx, _ in enumerate(s):
                    if ndx == 0:
                        md.write("| :-- ")
                    if ndx == len(s) - 1:
                        md.write("| :-- |")
                    else:
                        md.write("| :-- ")
                md.write(NEWLINE)

                write_row(s, md, "Report ID", lambda r: r.report_id)
                # write_row(s, md, "UEI", lambda r: r.general_information["auditee_uei"])
                write_row(s, md, "EIN", lambda r: r.general_information["ein"])
                write_row(
                    s,
                    md,
                    "Accepted",
                    lambda r: order_reports_key(r).strftime("%Y-%m-%d %H:%M:%S"),
                )
                write_row(
                    s,
                    md,
                    "Auditee name",
                    lambda r: r.general_information["auditee_name"],
                )
                write_row(
                    s,
                    md,
                    "Auditee email",
                    lambda r: r.general_information["auditee_email"],
                )
                write_row(
                    s,
                    md,
                    "Auditee state",
                    lambda r: r.general_information["auditee_state"],
                )

                md.write(NEWLINE)
                md.write(NEWLINE)


def export_mailmerge(AY, sets, noisy=False):
    with open(f"{AY}-mailmerge-{len(sets)}.csv", "w") as csv_file:
        wr = csv.writer(csv_file)  # , quoting=csv.QUOTE_ALL
        wr.writerow(
            [
                "audit_year",
                "initial_report_id",
                "initial_submission_date",
                "final_report_id",
                "final_submission_date",
                "auditee_uei",
                "auditee_ein",
                "auditee_entity",
                "auditee_contact_name",
                "auditee_email",
                "auditor_name",
                "auditor_email",
            ]
        )
        for ndx, s in enumerate(sets):
            if len(s) > 1:
                # Grab the last one. We've already decided they're
                # essentially the same records.
                r = sorted(s, key=order_reports_key)
                wr.writerow(
                    [
                        get_audit_year(r[0]),
                        r[0].report_id,
                        order_reports_key(r[0]).strftime("%Y-%m-%d"),
                        r[-1].report_id,
                        order_reports_key(r[-1]).strftime("%Y-%m-%d"),
                        r[-1].general_information["auditee_uei"],
                        r[-1].general_information["ein"],
                        prep_string(r[-1].general_information["auditee_name"]),
                        prep_string(r[-1].general_information["auditee_contact_name"]),
                        prep_string(r[-1].general_information["auditee_email"]),
                        prep_string(r[-1].general_information["auditor_name"]),
                        prep_string(r[-1].general_information["auditor_email"]),
                    ]
                )
