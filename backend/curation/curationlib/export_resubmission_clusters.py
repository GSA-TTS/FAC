import csv
import json
import os

from curation.curationlib.audit_distance import prep_string, get_audit_year

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _data_path(filename):
    """
    Return an absolute path inside the curation/data directory.
    Create the directory if it does not exist. It should always exist, but it doesn't hurt to verify.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, filename)


# All of the code in here is fiddly, and output-type
# code for inspection/analysis post-facto.

NEWLINE = "\n"


def order_reports_key(r):
    for ndx, tn in enumerate(list(reversed(r.transition_name))):
        if tn == "submitted":
            break
    return list(reversed(r.transition_date))[ndx]


# Exports the same data in CSV format for analysis in a spreadsheet tool.
def export_sets_as_csv(AY, sets, noisy=False):
    with open(_data_path(f"{AY}-resubmission-sets-{len(sets)}.csv"), "w") as csv_file:
        wr = csv.writer(csv_file)
        wr.writerow(
            [
                "set_index",
                # For distance-based matching. We may use this to catch more records in the future.
                # "set_distance",
                # "set_order",
                "report_id",
                "audit_year",
                "fac_accepted_date",
                "auditee_uei",
                "auditee_ein",
                "auditee_email",
                "auditee_name",
                "auditee_state",
                "prior_submission_status",
                "prior_resubmission_meta",
            ]
        )
        for ndx, s in enumerate(sets):
            if len(s) > 1:
                for r in sorted(s, key=order_reports_key):
                    wr.writerow(
                        [
                            ndx,
                            # r.distance,
                            # r.order,
                            r.report_id,
                            get_audit_year(r),
                            order_reports_key(r).strftime("%Y-%m-%d %H:%M:%S"),
                            r.general_information["auditee_uei"],
                            r.general_information["ein"],
                            prep_string(r.general_information["auditee_email"]),
                            prep_string(r.general_information["auditee_name"]),
                            prep_string(r.general_information["auditee_state"]),
                            r.submission_status,
                            (
                                json.dumps(r.resubmission_meta)
                                if r.resubmission_meta is not None
                                else ""
                            ),
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
    with open(_data_path(f"{AY}-resubmission-sets-{len(sets)}.md"), "w") as md:

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
                        md.write("| ... resubmitted as ")
                # We write a tag, and close. Hence extra pipes.
                md.write(" | ... resubmitted as |" + NEWLINE)

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


# export_mailmerge
# Leaving this function (though unused) for the moment.
# We *might* want to send notification to people whose records
# we modify. We might not (as it is within our remit to curate
# the record). This would spit out a CSV that we could use
# for that purpose. More conversation needed, but for the moment,
# lets leave this code here for reference.
def export_mailmerge(AY, sets, noisy=False):
    with open(_data_path(f"{AY}-mailmerge-{len(sets)}.csv"), "w") as csv_file:
        wr = csv.writer(csv_file)
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
