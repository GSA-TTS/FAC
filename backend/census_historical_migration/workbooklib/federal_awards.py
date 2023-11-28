from census_historical_migration.transforms.xform_string_to_string import (
    string_to_string,
)
from census_historical_migration.workbooklib.excel_creation_utils import (
    get_audit_header,
    get_audits,
    get_range_values,
    get_ranges,
    set_workbook_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
)
from census_historical_migration.base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from audit.fixtures.excel import FORM_SECTIONS
from config import settings
from census_historical_migration.models import (
    ELECAUDITS as Audits,
    ELECPASSTHROUGH as Passthrough,
)
from django.db.models import Q
import openpyxl as pyxl
import json

import logging

logger = logging.getLogger(__name__)


def if_zero_empty(v):
    if int(v) == 0:
        return ""
    else:
        return int(v)


mappings = [
    SheetFieldMap(
        "federal_agency_prefix", "CFDA_PREFIX", WorkbookFieldInDissem, None, str
    ),
    SheetFieldMap(
        "three_digit_extension", "CFDA_EXT", "federal_award_extension", None, str
    ),
    SheetFieldMap(
        "program_name", "FEDERALPROGRAMNAME", "federal_program_name", None, str
    ),
    SheetFieldMap(
        "state_cluster_name", "STATECLUSTERNAME", WorkbookFieldInDissem, None, str
    ),
    SheetFieldMap(
        "federal_program_total", "PROGRAMTOTAL", WorkbookFieldInDissem, 0, int
    ),
    SheetFieldMap(
        "additional_award_identification",
        "AWARDIDENTIFICATION",
        WorkbookFieldInDissem,
        None,
        str,
    ),
    SheetFieldMap("cluster_total", "CLUSTERTOTAL", WorkbookFieldInDissem, 0, int),
    SheetFieldMap("is_guaranteed", "LOANS", "is_loan", None, str),
    # In the intake process, we initially use convert_to_stripped_string to convert IR values into strings,
    # and then apply specific functions like convert_loan_balance_to_integers_or_na to convert particular fields
    # such as loan_balance_at_audit_period_end into their appropriate formats. Therefore, it's suitable to process
    # this column as a string here because treating it as an integer would be incorrect due to the presence of 'N/A' values.
    # Any values like 'n/a', if present, may initially fail to process but will be addressed through data transformation
    # in subsequent iterations of the data migration process.
    SheetFieldMap(
        "loan_balance_at_audit_period_end", "LOANBALANCE", "loan_balance", None, str
    ),
    SheetFieldMap("is_direct", "DIRECT", WorkbookFieldInDissem, None, str),
    SheetFieldMap("is_passed", "PASSTHROUGHAWARD", "is_passthrough_award", None, str),
    SheetFieldMap(
        "subrecipient_amount",
        "PASSTHROUGHAMOUNT",
        "passthrough_amount",
        None,
        if_zero_empty,
    ),
    SheetFieldMap("is_major", "MAJORPROGRAM", WorkbookFieldInDissem, None, str),
    SheetFieldMap("audit_report_type", "TYPEREPORT_MP", "audit_report_type", None, str),
    SheetFieldMap(
        "number_of_audit_findings", "FINDINGSCOUNT", "findings_count", 0, int
    ),
    SheetFieldMap("amount_expended", "AMOUNT", WorkbookFieldInDissem, 0, int),
]


def get_list_index(all_items, index):
    counter = 0
    for item in list(all_items):
        if item.ID == index:
            return counter
        else:
            counter += 1
    return -1


def _generate_cluster_names(
    audits: list[Audits],
) -> tuple[list[str], list[str], list[str]]:
    """Reconstructs the cluster names for each audit in the provided list."""
    # Patch the clusternames. They used to be allowed to enter anything
    # they wanted.
    valid_file = open(f"{settings.BASE_DIR}/schemas/source/base/ClusterNames.json")
    valid_json = json.load(valid_file)
    cluster_names = []
    state_cluster_names = []
    other_cluster_names = []
    for audit in audits:
        cluster_name = string_to_string(audit.CLUSTERNAME)
        if not cluster_name:
            cluster_names.append("N/A")
            other_cluster_names.append("")
            state_cluster_names.append("")
        elif cluster_name == "STATE CLUSTER":
            cluster_names.append(cluster_name)
            state_cluster_names.append(audit.STATECLUSTERNAME)
            other_cluster_names.append("")
        elif cluster_name == "OTHER CLUSTER NOT LISTED ABOVE":
            cluster_names.append(cluster_name)
            other_cluster_names.append(audit.OTHERCLUSTERNAME)
            state_cluster_names.append("")
        elif cluster_name in valid_json["cluster_names"]:
            cluster_names.append(cluster_name)
            other_cluster_names.append("")
            state_cluster_names.append("")
        else:
            logger.debug(f"Cluster {cluster_name} not in the list. Replacing.")
            cluster_names.append("OTHER CLUSTER NOT LISTED ABOVE")
            other_cluster_names.append(f"{cluster_name}")
            state_cluster_names.append("")
    return (cluster_names, other_cluster_names, state_cluster_names)


def _get_full_cfdas(audits):
    """
    This function constructs the full CFDA numbers by concatenating the CFDA_PREFIX
    and CFDA_EXT attributes of each audit object, separated by a dot.
    """
    # audit.CFDA is not used here because it does not always match f"{audit.CFDA_PREFIX}.{audit.CFDA_EXT}"
    return [f"{audit.CFDA_PREFIX}.{audit.CFDA_EXT}" for audit in audits]


# The functionality of _fix_passthroughs has been split into two separate functions:
# _get_passthroughs and _xform_populate_default_passthrough_values. Currently, _get_passthroughs is being
# used in place of _fix_passthroughs.
def _get_passthroughs(audits):
    """
    Retrieves the passthrough names and IDs for a given list of audits.
    For each audit in the provided list, this function queries the Passthrough model to find
    records matching the DBKEY and ELECAUDITSID of the audit. It then compiles lists of
    passthrough names and IDs, joined by a pipe '|' if multiple are found.
    """
    passthrough_names = [""] * len(audits)
    passthrough_ids = [""] * len(audits)

    for index, audit in enumerate(audits):
        passthroughs = Passthrough.objects.filter(
            DBKEY=audit.DBKEY, ELECAUDITSID=audit.ELECAUDITSID
        ).order_by("ID")
        # This may look like data transformation but it is not exactly the case.
        # In the audit worksheet, users can enter multiple names (or IDs) separated by a pipe '|' in a single cell.
        # We are simply reconstructing this pipe separated data here.
        names = []
        ids = []
        for passthrough in passthroughs:
            passthrough_name = string_to_string(passthrough.PASSTHROUGHNAME)
            passthrough_id = string_to_string(passthrough.PASSTHROUGHID)
            if passthrough_name:
                names.append(passthrough_name)
            if passthrough_id:
                ids.append(passthrough_id)

        passthrough_names[index] = "|".join(names) if names else ""
        passthrough_ids[index] = "|".join(ids) if ids else ""
    return (passthrough_names, passthrough_ids)


# FIXME - MSHD: _xform_populate_default_passthrough_values is currently unused as unrequired data transformation
# will not be part of the first iteration of the data migration process.
# Only required (MUST) data transformation will be part of the first iteration.
def _xform_populate_default_passthrough_values(
    passthrough_names, passthrough_ids, audits
):
    """
    Automatically fills in default values for empty passthrough names and IDs.
    Iterates over a list of audits and their corresponding passthrough names and IDs.
    If the audit's DIRECT attribute is "N" and the passthrough name or ID is empty,
    it fills in a default value indicating that no passthrough name or ID was provided.
    """
    for index, audit, name, id in zip(
        range(len(audits)), audits, passthrough_names, passthrough_ids
    ):
        if audit.DIRECT == "N" and name == "":
            passthrough_names[index] = "NO PASSTHROUGH NAME PROVIDED"
        if audit.DIRECT == "N" and id == "":
            passthrough_ids[index] = "NO PASSTHROUGH ID PROVIDED"
    return (passthrough_names, passthrough_ids)


# FIXME - MSHD: _xform_populate_default_loan_balance is currently unused
# as unrequired data transformation will not be part of the first iteration
# of the data migration process.
def _xform_populate_default_loan_balance(loans_at_end, audits):
    """
    Automatically fills in default values for empty loan balances.
    Iterates over a list of audits and their corresponding loan balances.
    If the audit's LOANS attribute is "Y" and the loan balance is empty,
    it fills in a default value indicating that no loan balance was provided."""
    for ndx, audit in zip(range(len(audits)), audits, loans_at_end):
        if audit.LOANS == "Y":
            if audit.LOANBALANCE is None:
                loans_at_end[
                    ndx
                ] = 1  # FIXME - MSHD: This value requires team approval.
                # There are cases (dbkeys 148665/150450) with balance = -1.0, how do we handle this?
        else:
            if audit.LOANBALANCE is not None:
                loans_at_end[ndx] = ""
    return loans_at_end


# FIXME - MSHD: _xform_populate_default_award_identification_values is currently unused
# as unrequired data transformation will not be part of the first iteration
# of the data migration process.
def _xform_populate_default_award_identification_values(audits, dbkey):
    """
    Automatically fills in default values for empty additional award identifications.
    Iterates over a list of audits and their corresponding additional award identifications.
    If the audit's CFDA attribute contains "U" or "u" or "rd" or "RD" and the award identification is empty,
    it fills in a default value indicating that no award identification was provided.
    """
    addl_award_identifications = [""] * len(audits)
    filtered_audits = Audits.objects.filter(
        Q(DBKEY=dbkey) & (Q(CFDA__icontains="U") | Q(CFDA__icontains="rd"))
    ).order_by("ID")
    for audit in filtered_audits:
        if audit.AWARDIDENTIFICATION is None or len(audit.AWARDIDENTIFICATION) < 1:
            addl_award_identifications[
                get_list_index(audits, audit.ID)
            ] = f"ADDITIONAL AWARD INFO - DBKEY {dbkey}"
        else:
            addl_award_identifications[
                get_list_index(audits, audit.ID)
            ] = audit.AWARDIDENTIFICATION
    return addl_award_identifications


def generate_federal_awards(dbkey, year, outfile):
    """
    Generates a federal awards workbook for all awards associated with a given dbkey.

    Note: This function assumes that all the audit information in the database
    is for the same year.
    """
    logger.info(f"--- generate federal awards {dbkey} {year} ---")

    wb = pyxl.load_workbook(
        sections_to_template_paths[FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED]
    )

    audit_header = get_audit_header(dbkey)

    set_workbook_uei(wb, audit_header.UEI)

    audits = get_audits(dbkey)

    map_simple_columns(wb, mappings, audits)

    (cluster_names, other_cluster_names, state_cluster_names) = _generate_cluster_names(
        audits
    )
    set_range(wb, "cluster_name", cluster_names)
    set_range(wb, "other_cluster_name", other_cluster_names)

    # We need a `cfda_key` as a magic column for the summation logic to work/be checked.
    full_cfdas = _get_full_cfdas(audits)
    set_range(wb, "cfda_key", full_cfdas, conversion_fun=str)

    # We need `uniform_state_cluster_name` and `uniform_other_cluster_name` magic columns for cluster summation logic to work/be checked.
    set_range(
        wb,
        "uniform_state_cluster_name",
        [s.strip().upper() for s in state_cluster_names],
        conversion_fun=str,
    )
    set_range(
        wb,
        "uniform_other_cluster_name",
        [s.strip().upper() for s in other_cluster_names],
        conversion_fun=str,
    )

    (passthrough_names, passthrough_ids) = _get_passthroughs(audits)

    set_range(wb, "passthrough_name", passthrough_names)
    set_range(wb, "passthrough_identifying_number", passthrough_ids)

    # The award numbers!
    set_range(
        wb,
        "award_reference",
        [f"AWARD-{n+1:04}" for n in range(len(audits))],
    )

    # Total amount expended must be calculated and inserted
    total = 0
    for audit in audits:
        total += int(audit.AMOUNT)
    set_range(wb, "total_amount_expended", [str(total)])

    wb.save(outfile)

    # FIXME - MSHD: The test table and the logic around it do not seem necessary to me.
    # If there is any chance that the dissemination process allows bogus data to be disseminated,
    # we should fix the dissemination process instead by reinforcing the validation logic (intake validation and cross-validation).
    # I will create a ticket for the removal of this logic unless someone comes up with a strong reason to keep it.
    table = generate_dissemination_test_table(
        audit_header, "federal_awards", dbkey, mappings, audits
    )
    award_counter = 1
    filtered_mappings = [
        mapping
        for mapping in mappings
        if mapping.in_sheet
        in [
            "additional_award_identification",
            "federal_agency_prefix",
            "three_digit_extension",
        ]
    ]
    ranges = get_ranges(filtered_mappings, audits)
    prefixes = get_range_values(ranges, "federal_agency_prefix")
    extensions = get_range_values(ranges, "three_digit_extension")
    additional_award_identifications = get_range_values(
        ranges, "additional_award_identification"
    )
    # prefix
    for (
        award,
        prefix,
        extension,
        additional_identification,
        cluster_name,
        other_cluster_name,
    ) in zip(
        table["rows"],
        prefixes,
        extensions,
        additional_award_identifications,
        cluster_names,
        other_cluster_names,
    ):
        award["fields"].append("federal_agency_prefix")
        award["values"].append(prefix)
        award["fields"].append("three_digit_extension")
        award["values"].append(extension)
        # Sneak in the award number here
        award["fields"].append("award_reference")
        award["values"].append(f"AWARD-{award_counter:04}")
        award["fields"].append("additional_award_identification")
        award["values"].append(additional_identification)
        award["fields"].append("cluster_name")
        award["values"].append(cluster_name)
        award["fields"].append("other_cluster_name")
        award["fields"].append(other_cluster_name)
        award_counter += 1

    table["singletons"]["auditee_uei"] = audit_header.UEI
    table["singletons"]["total_amount_expended"] = total

    return (wb, table)
