from audit.intakelib.checks.check_cluster_total import expected_cluster_total
from ..transforms.xform_string_to_int import string_to_int
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..exception_utils import DataMigrationError
from ..transforms.xform_string_to_string import (
    string_to_string,
)
from .excel_creation_utils import (
    get_audits,
    set_workbook_uei,
    map_simple_columns,
    set_range,
    sort_by_field,
    track_transformations,
)
from ..base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from .templates import sections_to_template_paths
from audit.fixtures.excel import FORM_SECTIONS
from django.conf import settings
from ..models import (
    ELECAUDITS as Audits,
    ELECPASSTHROUGH as Passthrough,
)
from ..change_record import (
    CensusRecord,
    InspectionRecord,
    GsaFacRecord,
)

import openpyxl as pyxl

import logging
import re


logger = logging.getLogger(__name__)


mappings = [
    SheetFieldMap(
        "federal_agency_prefix", "CFDA_PREFIX", WorkbookFieldInDissem, None, str
    ),
    SheetFieldMap(
        "program_name", "FEDERALPROGRAMNAME", "federal_program_name", None, str
    ),
    SheetFieldMap(
        "state_cluster_name", "STATECLUSTERNAME", WorkbookFieldInDissem, None, str
    ),
    SheetFieldMap(
        "federal_program_total", "PROGRAMTOTAL", WorkbookFieldInDissem, None, int
    ),
    SheetFieldMap(
        "additional_award_identification",
        "AWARDIDENTIFICATION",
        WorkbookFieldInDissem,
        None,
        str,
    ),
    SheetFieldMap("cluster_total", "CLUSTERTOTAL", WorkbookFieldInDissem, None, int),
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
        str,
    ),
    SheetFieldMap("is_major", "MAJORPROGRAM", WorkbookFieldInDissem, None, str),
    SheetFieldMap("audit_report_type", "TYPEREPORT_MP", "audit_report_type", None, str),
    SheetFieldMap(
        "number_of_audit_findings", "FINDINGSCOUNT", "findings_count", None, int
    ),
    SheetFieldMap("amount_expended", "AMOUNT", WorkbookFieldInDissem, None, int),
]


def xform_missing_findings_count(audits):
    """Default missing findings count to zero."""
    # Transformation to be documented.
    for audit in audits:
        findings_count = string_to_string(audit.FINDINGSCOUNT)
        if not findings_count:
            audit.FINDINGSCOUNT = "0"


def xform_missing_amount_expended(audits):
    """Default missing amount expended to zero."""
    # Transformation recorded.
    change_records = []
    is_empty_amount_expended_found = False
    for audit in audits:
        amount = string_to_string(audit.AMOUNT)
        if not amount:
            is_empty_amount_expended_found = True

        amount = string_to_int(amount) if amount else 0

        track_transformations(
            "AMOUNT",
            audit.AMOUNT,
            "amount_expended",
            amount,
            ["xform_missing_amount_expended"],
            change_records,
        )
        audit.AMOUNT = str(amount)

    if change_records and is_empty_amount_expended_found:
        InspectionRecord.append_federal_awards_changes(change_records)


def xform_missing_program_total(audits):
    """Calculates missing program total for each award."""
    program_totals = {}
    for audit in audits:
        cfda_key = (
            f"{string_to_string(audit.CFDA_PREFIX)}.{string_to_string(audit.CFDA_EXT)}"
        )
        amount = string_to_int(audit.AMOUNT) if string_to_string(audit.AMOUNT) else 0
        if cfda_key in program_totals:
            program_totals[cfda_key] = program_totals[cfda_key] + amount
        else:
            program_totals[cfda_key] = amount

    change_records = []
    is_empty_program_total_found = False

    for audit in audits:
        program_total = string_to_string(audit.PROGRAMTOTAL)
        cfda_key = (
            f"{string_to_string(audit.CFDA_PREFIX)}.{string_to_string(audit.CFDA_EXT)}"
        )
        if not program_total:
            is_empty_program_total_found = True

        # Only use calculated program_total when program_total is empty
        program_total = (
            string_to_int(program_total) if program_total else program_totals[cfda_key]
        )
        track_transformations(
            "PROGRAMTOTAL",
            audit.PROGRAMTOTAL,
            "federal_program_total",
            program_total,
            ["xform_missing_program_total"],
            change_records,
        )
        audit.PROGRAMTOTAL = str(program_total)

    if change_records and is_empty_program_total_found:
        InspectionRecord.append_federal_awards_changes(change_records)


def xform_missing_cluster_total(
    audits,
    cluster_names,
    other_cluster_names,
    state_cluster_names,
):
    """Calculates missing cluster total for each award."""
    uniform_state_cluster_names = [name.upper() for name in state_cluster_names]
    uniform_other_cluster_names = [name.upper() for name in other_cluster_names]
    amounts_expended = [
        string_to_int(audit.AMOUNT) if string_to_string(audit.AMOUNT) else 0
        for audit in audits
    ]

    change_records = []
    is_empty_cluster_total_found = False
    for idx, (name, audit) in enumerate(zip(cluster_names, audits)):
        cluster_total = string_to_string(audit.CLUSTERTOTAL)
        if not cluster_total:
            is_empty_cluster_total_found = True

        # Only use calculated cluster_total when cluster_total is empty
        if cluster_total:
            cluster_total = string_to_int(cluster_total)
        else:
            cluster_total = expected_cluster_total(
                idx=idx,
                name=name,
                uniform_other_cluster_names=uniform_other_cluster_names,
                uniform_state_cluster_names=uniform_state_cluster_names,
                state_cluster_names=state_cluster_names,
                cluster_names=cluster_names,
                amounts_expended=amounts_expended,
            )

        track_transformations(
            "CLUSTERTOTAL",
            audit.CLUSTERTOTAL,
            "cluster_total",
            cluster_total,
            ["xform_missing_cluster_total"],
            change_records,
        )
        audit.CLUSTERTOTAL = str(cluster_total)

    if change_records and is_empty_cluster_total_found:
        InspectionRecord.append_federal_awards_changes(change_records)


def xform_is_passthrough_award(audits):
    """
    Replaces missing PASSTHROUGHAWARD field with GSA_MIGRATION
    """
    change_records = []
    is_empty_passthrough_found = False

    for audit in audits:
        if audit.PASSTHROUGHAWARD.strip() == "":
            is_empty_passthrough_found = True

            track_transformations(
                "PASSTHROUGHAWARD",
                "",
                "is_passthrough_award",
                settings.GSA_MIGRATION,
                "xform_is_passthrough_award",
                change_records,
            )
            
            audit.PASSTHROUGHAWARD = settings.GSA_MIGRATION

    if change_records and is_empty_passthrough_found:
        InspectionRecord.append_federal_awards_changes(change_records)


def xform_constructs_cluster_names(
    audits: list[Audits],
) -> tuple[list[str], list[str], list[str]]:
    """Reconstructs the cluster names for each audit in the provided list."""

    cluster_names = []
    state_cluster_names = []
    other_cluster_names = []
    for audit in audits:
        cluster_name = string_to_string(audit.CLUSTERNAME)
        state_cluster_name = string_to_string(audit.STATECLUSTERNAME)
        other_cluster_name = string_to_string(audit.OTHERCLUSTERNAME)
        # Default values for clusters
        cluster_names.append(cluster_name if cluster_name else settings.GSA_MIGRATION)
        state_cluster_names.append(state_cluster_name if state_cluster_name else "")
        other_cluster_names.append(other_cluster_name if other_cluster_name else "")

        # Handling specific cases
        if cluster_name == settings.STATE_CLUSTER:
            state_cluster_names[-1] = (
                state_cluster_name if state_cluster_name else settings.GSA_MIGRATION
            )
        elif cluster_name == settings.OTHER_CLUSTER:
            other_cluster_names[-1] = (
                other_cluster_name if other_cluster_name else settings.GSA_MIGRATION
            )
        elif not cluster_name and (state_cluster_name or other_cluster_name):
            # Already handled by default values
            pass
        elif cluster_name and (state_cluster_name or other_cluster_name):
            # MSHD - 12/14/2023: If we want to let these cases through,
            # we must modify state_cluster_names and other_cluster_names
            # methods in check_state_cluster_names.py and check_other_cluster_names.py (intakelib/checks).
            raise DataMigrationError(
                "Unable to determine cluster name.", "invalid_cluster"
            )

    # Create Census_data, gsa_fac_data

    return (cluster_names, other_cluster_names, state_cluster_names)


def is_valid_prefix(prefix):
    """
    Checks if the provided prefix is a valid CFDA prefix.
    """
    return re.match(settings.REGEX_ALN_PREFIX, str(prefix))


def _extract_extensions(full_cfdas):
    """Extracts the extensions from a list of CFDA keys."""
    return [s.split(".")[1] for s in full_cfdas if "." in s]


def is_valid_extension(extension):
    """
    Checks if the provided extension is a valid CFDA extension.
    """
    # Define regex patterns
    patterns = [
        settings.REGEX_RD_EXTENSION,
        settings.REGEX_THREE_DIGIT_EXTENSION,
        settings.REGEX_U_EXTENSION,
    ]
    return any(re.match(pattern, str(extension)) for pattern in patterns)


def xform_replace_invalid_extension(audit):
    """Replaces invalid ALN extensions with the default value settings.GSA_MIGRATION."""
    prefix = string_to_string(audit.CFDA_PREFIX)
    extension = string_to_string(audit.CFDA_EXT)
    if not is_valid_prefix(prefix):
        raise DataMigrationError(f"Invalid ALN prefix: {prefix}", "invalid_aln_prefix")
    if not is_valid_extension(extension):
        extension = settings.GSA_MIGRATION

    cfda_key = f"{prefix}.{extension}"

    transformation_record = {
        "census_data": [CensusRecord("CFDA_EXT", audit.CFDA_EXT).to_dict()],
        "gsa_fac_data": GsaFacRecord("federal_award_extension", extension).to_dict(),
        "transformation_functions": ["xform_replace_invalid_extension"],
    }

    return cfda_key, transformation_record


def _get_full_cfdas(audits):
    """
    This function constructs the full CFDA numbers by concatenating the CFDA_PREFIX
    and CFDA_EXT attributes of each audit object, separated by a dot.
    """
    cfdas = []
    transformations = []
    for audit in audits:
        full_cfda, transformation = xform_replace_invalid_extension(audit)
        cfdas.append(full_cfda)
        transformations.append(transformation)
    if transformations:
        InspectionRecord.append_federal_awards_changes(transformations)
    return cfdas


def _get_passthroughs(audits):
    """
    Retrieves the passthrough names and IDs for a given list of audits.
    For each audit in the provided list, this function queries the Passthrough model to find
    records matching the DBKEY and ELECAUDITSID of the audit. It then compiles lists of
    passthrough names and IDs, joined by a pipe '|' if multiple are found.
    """
    passthrough_names = ["" for _ in audits]
    passthrough_ids = ["" for _ in audits]

    for index, audit in enumerate(audits):
        passthroughs = Passthrough.objects.filter(
            DBKEY=audit.DBKEY,
            AUDITYEAR=audit.AUDITYEAR,
            ELECAUDITSID=audit.ELECAUDITSID,
        )
        passthroughs = sort_by_field(passthroughs, "ID")
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


def xform_match_number_passthrough_names_ids(names, ids):
    """
    Matches the number of passthrough names and IDs.
    Iterates over a list of passthrough names and IDs.
    If the number of passthrough names is greater than the number of passthrough IDs,
    it fills in the missing passthrough IDs with `NA`.
    """
    # Transformation to be documented.
    for idx, (name, id) in enumerate(zip(names, ids)):
        passthrough_names = name.split("|")
        passthrough_ids = id.split("|")
        length_difference = len(passthrough_names) - len(passthrough_ids)
        if length_difference > 0:
            patch = [settings.GSA_MIGRATION for _ in range(length_difference)]
            if id == "":
                patch.append(settings.GSA_MIGRATION)
                ids[idx] = "|".join(patch)
            else:
                passthrough_ids.extend(patch)
                ids[idx] = "|".join(passthrough_ids)

    return names, ids


def xform_populate_default_passthrough_names_ids(audits):
    """
    Retrieves the passthrough names and IDs for a given list of audits.
    Automatically fills in default values for empty passthrough names and IDs.
    Iterates over a list of audits and their corresponding passthrough names and IDs.
    If the audit's DIRECT attribute is "N" and the passthrough name or ID is empty,
    it fills in a default value indicating that no passthrough name or ID was provided.
    """
    # Transformation to be documented.
    passthrough_names, passthrough_ids = _get_passthroughs(audits)
    passthrough_names, passthrough_ids = xform_match_number_passthrough_names_ids(
        passthrough_names, passthrough_ids
    )
    for index, audit, name, id in zip(
        range(len(audits)), audits, passthrough_names, passthrough_ids
    ):
        direct = string_to_string(audit.DIRECT)
        if direct == "N" and name == "":
            passthrough_names[index] = settings.GSA_MIGRATION
        if direct == "N" and id == "":
            passthrough_ids[index] = settings.GSA_MIGRATION
    return (passthrough_names, passthrough_ids)


def xform_populate_default_loan_balance(audits):
    """
    Automatically fills in default values for empty loan balances.
    Iterates over a list of audits and their corresponding loan balances.
    If the audit's LOANS attribute is "Y" and the loan balance is empty,
    it fills in a default value indicating that no loan balance was provided."""
    loans_at_end = []

    for audit in audits:
        loan = string_to_string(audit.LOANS).upper()
        balance = string_to_string(audit.LOANBALANCE)
        if loan == "Y":
            if balance:
                loans_at_end.append(balance)
            else:
                loans_at_end.append(
                    settings.GSA_MIGRATION
                )  # transformation to be documented
        else:
            if balance and balance != "0":
                raise DataMigrationError(
                    "Unexpected loan balance.", "unexpected_loan_balance"
                )
            else:
                loans_at_end.append("")  # transformation to be documented

    return loans_at_end


def xform_populate_default_award_identification_values(audits):
    """
    Automatically fills in default values for empty additional award identifications.
    Iterates over a list of audits and their corresponding additional award identifications.
    If the audit's CFDA attribute contains "U" or "u" or "rd" or "RD" and the award identification is empty,
    it fills in a default value indicating that no award identification was provided.
    """
    addl_award_identifications = []

    for audit in audits:
        cfda = string_to_string(audit.CFDA).upper()
        identification = string_to_string(audit.AWARDIDENTIFICATION)

        if re.search(r"U|RD", cfda) and not identification:
            addl_award_identifications.append(settings.GSA_MIGRATION)
        else:
            addl_award_identifications.append(identification)

    return addl_award_identifications


def xform_populate_default_passthrough_amount(audits):
    """
    Automatically fills in default values for empty passthrough amounts.
    Iterates over a list of audits and their corresponding passthrough amounts.
    If the audit's PASSTHROUGHAWARD attribute is "Y" and the passthrough amount is empty,
    it fills in a default value indicating that no passthrough amount was provided.
    """
    passthrough_amounts = []

    for audit in audits:
        passthrough_award = string_to_string(audit.PASSTHROUGHAWARD).upper()
        amount = string_to_string(audit.PASSTHROUGHAMOUNT)
        if passthrough_award == "Y":
            if amount:
                passthrough_amounts.append(amount)
            else:
                passthrough_amounts.append(str(settings.GSA_MIGRATION_INT))
        else:
            if not amount or amount == "0":
                passthrough_amounts.append("")
            else:
                raise DataMigrationError(
                    "Unexpected passthrough amount.", "unexpected_passthrough_amount"
                )

    return passthrough_amounts


def generate_federal_awards(audit_header, outfile):
    """
    Generates a federal awards workbook for all awards associated with a given audit header.
    """
    logger.info(
        f"--- generate federal awards {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )

    wb = pyxl.load_workbook(
        sections_to_template_paths[FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED]
    )
    uei = xform_retrieve_uei(audit_header.UEI)
    set_workbook_uei(wb, uei)
    audits = get_audits(audit_header.DBKEY, audit_header.AUDITYEAR)

    (
        cluster_names,
        other_cluster_names,
        state_cluster_names,
    ) = xform_constructs_cluster_names(audits)

    xform_missing_cluster_total(
        audits, cluster_names, other_cluster_names, state_cluster_names
    )
    xform_missing_program_total(audits)
    xform_missing_findings_count(audits)
    xform_missing_amount_expended(audits)
    xform_is_passthrough_award(audits)

    map_simple_columns(wb, mappings, audits)

    set_range(wb, "cluster_name", cluster_names)
    set_range(wb, "other_cluster_name", other_cluster_names)
    set_range(wb, "state_cluster_name", state_cluster_names)

    # We need a `cfda_key` as a magic column for the summation logic to work/be checked.
    full_cfdas = _get_full_cfdas(audits)
    set_range(wb, "cfda_key", full_cfdas, conversion_fun=str)
    extensions = _extract_extensions(full_cfdas)
    set_range(wb, "three_digit_extension", extensions, conversion_fun=str)
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

    (passthrough_names, passthrough_ids) = xform_populate_default_passthrough_names_ids(
        audits
    )
    set_range(wb, "passthrough_name", passthrough_names)
    set_range(wb, "passthrough_identifying_number", passthrough_ids)

    # The award numbers!
    set_range(
        wb,
        "award_reference",
        [f"AWARD-{n+1:04}" for n in range(len(audits))],
    )

    # passthrough amount
    passthrough_amounts = xform_populate_default_passthrough_amount(audits)
    set_range(wb, "subrecipient_amount", passthrough_amounts)

    # additional award identification
    additional_award_identifications = (
        xform_populate_default_award_identification_values(audits)
    )
    set_range(
        wb,
        "additional_award_identification",
        additional_award_identifications,
    )

    # loan balance at audit period end
    loan_balances = xform_populate_default_loan_balance(audits)
    set_range(
        wb,
        "loan_balance_at_audit_period_end",
        loan_balances,
    )

    # Total amount expended must be calculated and inserted
    total = 0
    for audit in audits:
        total += int(audit.AMOUNT)
    set_range(wb, "total_amount_expended", [str(total)])
    wb.save(outfile)

    return wb
