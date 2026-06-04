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
def export_chains_as_csv(chains, AY=None, report_ids=None, noisy=False):
    filename = _data_path(
        f"{AY or report_ids[0]}-resubmission-chains-{len(chains)}.csv"
    )

    with open(filename, "w") as csv_file:
        wr = csv.writer(csv_file)
        wr.writerow(
            [
                "chain_index",
                # For distance-based matching. We may use this to catch more records in the future.
                # "distance",
                # "order",
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
        for ndx, chain in enumerate(chains):
            if len(chain) > 1:
                for r in sorted(chain, key=order_reports_key):
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
    return filename


def write_row(chain, md, row_tag, key_fun):
    md.write(f"| {row_tag} ")

    for ndx, r in enumerate(sorted(chain, key=order_reports_key)):
        # Printing data is annoying.
        FIRST = ndx == 0
        LAST = ndx == len(chain) - 1

        md.write("| ")
        md.write(key_fun(r))

        if LAST and not FIRST:
            md.write(" |")
    md.write(NEWLINE)


def export_chains_as_markdown(chains, AY=None, report_ids=None):
    """
    Exports the chain data as Markdown for use on the WWW.

    Returns the path to the file.
    """
    filename = _data_path(f"{AY or report_ids[0]}-resubmission-chains-{len(chains)}.md")
    title = (
        f"### Resubmissions for {f"audit year {AY}" if AY else report_ids[0]}"
        + NEWLINE
        + NEWLINE
    )

    with open(filename, "w") as md:
        md.write(title)

        for ndx, chain in enumerate(chains):
            if len(chain) > 1:
                md.write(
                    f"#### UEI {chain[0].general_information['auditee_uei']}" + NEWLINE
                )
                for ndx, _ in enumerate(chain):
                    if ndx in [0, 1]:
                        md.write("| ")
                    else:
                        md.write("| ... resubmitted as ")
                # We write a tag, and close. Hence extra pipes.
                md.write(" | ... resubmitted as |" + NEWLINE)

                for ndx, _ in enumerate(chain):
                    if ndx == 0:
                        md.write("| :-- ")
                    if ndx == len(chain) - 1:
                        md.write("| :-- |")
                    else:
                        md.write("| :-- ")
                md.write(NEWLINE)

                write_row(chain, md, "Report ID", lambda r: r.report_id)
                # write_row(chain, md, "UEI", lambda r: r.general_information["auditee_uei"])
                write_row(chain, md, "EIN", lambda r: r.general_information["ein"])
                write_row(
                    chain,
                    md,
                    "Accepted",
                    lambda r: order_reports_key(r).strftime("%Y-%m-%d %H:%M:%S"),
                )
                write_row(
                    chain,
                    md,
                    "Auditee name",
                    lambda r: r.general_information["auditee_name"],
                )
                write_row(
                    chain,
                    md,
                    "Auditee email",
                    lambda r: r.general_information["auditee_email"],
                )
                write_row(
                    chain,
                    md,
                    "Auditee state",
                    lambda r: r.general_information["auditee_state"],
                )

                md.write(NEWLINE)
                md.write(NEWLINE)

    return filename


# export_mailmerge
# Leaving this function (though unused) for the moment.
# We *might* want to send notification to people whose records
# we modify. We might not (as it is within our remit to curate
# the record). This would spit out a CSV that we could use
# for that purpose. More conversation needed, but for the moment,
# lets leave this code here for reference.
def export_mailmerge(AY, chains, noisy=False):
    with open(_data_path(f"{AY}-mailmerge-{len(chains)}.csv"), "w") as csv_file:
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
        for ndx, chain in enumerate(chains):
            if len(chain) > 1:
                # Grab the last one. We've already decided they're
                # essentially the same records.
                r = sorted(chain, key=order_reports_key)
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
