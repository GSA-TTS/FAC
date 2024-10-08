from collections import defaultdict
from audit.intakelib.checks.check_cluster_total import expected_cluster_total
from .findings import get_findings
from ..invalid_migration_tags import INVALID_MIGRATION_TAGS
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..transforms.xform_string_to_int import string_to_int
from ..transforms.xform_string_to_string import string_to_string
from ..transforms.xform_uppercase_y_or_n import uppercase_y_or_n
from ..exception_utils import DataMigrationError
from .excel_creation_utils import (
    get_audits,
    get_range_values,
    set_workbook_uei,
    map_simple_columns,
    set_range,
    sort_by_field,
    track_invalid_records,
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
from ..invalid_record import InvalidRecord
import openpyxl as pyxl

import logging
import re


logger = logging.getLogger(__name__)

# Transformation Method Change Recording
# For the purpose of recording changes, the transformation methods (i.e., xform_***)
# below track all records related to the federal_awards section that undergoes transformation and
# log these changes in a temporary array called `change_records`.
# However, we only save this data into the InspectionRecord table if at least one of the records has been
# modified by the transformation. If no records related to the given section
# were modified, then we do not save `change_records` into the InspectionRecord.


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
    SheetFieldMap("is_guaranteed", "LOANS", "is_loan", None, uppercase_y_or_n),
    # In the intake process, we initially use convert_to_stripped_string to convert IR values into strings,
    # and then apply specific functions like convert_loan_balance_to_integers_or_na to convert particular fields
    # such as loan_balance_at_audit_period_end into their appropriate formats. Therefore, it's suitable to process
    # this column as a string here because treating it as an integer would be incorrect due to the presence of 'N/A' values.
    # Any values like 'n/a', if present, may initially fail to process but will be addressed through data transformation
    # in subsequent iterations of the data migration process.
    SheetFieldMap(
        "loan_balance_at_audit_period_end", "LOANBALANCE", "loan_balance", None, str
    ),
    SheetFieldMap("is_passed", "PASSTHROUGHAWARD", "is_passthrough_award", None, str),
    SheetFieldMap(
        "subrecipient_amount",
        "PASSTHROUGHAMOUNT",
        "passthrough_amount",
        None,
        str,
    ),
    SheetFieldMap(
        "is_major", "MAJORPROGRAM", WorkbookFieldInDissem, None, uppercase_y_or_n
    ),
    SheetFieldMap("audit_report_type", "TYPEREPORT_MP", "audit_report_type", None, str),
    SheetFieldMap(
        "number_of_audit_findings", "FINDINGSCOUNT", "findings_count", None, int
    ),
    SheetFieldMap("amount_expended", "AMOUNT", WorkbookFieldInDissem, None, int),
]


def xform_missing_major_program(audits):
    """Default missing major program by extrapolating from audit report type."""
    change_records = []
    is_empty_major_program_found = False

    for audit in audits:
        major_program = string_to_string(audit.MAJORPROGRAM)
        if not major_program:
            major_program = "Y" if string_to_string(audit.TYPEREPORT_MP) else "N"
            is_empty_major_program_found = True

        track_transformations(
            "MAJORPROGRAM",
            audit.MAJORPROGRAM,
            "is_major",
            major_program,
            ["xform_missing_major_program"],
            change_records,
        )

        audit.MAJORPROGRAM = major_program

    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_empty_major_program_found:
        InspectionRecord.append_federal_awards_changes(change_records)


def track_invalid_number_of_audit_findings(audits, audit_header):
    """Track invalid number of audit findings."""
    findings = get_findings(audit_header.DBKEY, audit_header.AUDITYEAR)

    invalid_audit_records = []
    is_incorrect_findings_count_found = False
    expected_finding_count = defaultdict(int)
    declared_finding_count = defaultdict(int)

    # Count the expected findings
    for finding in findings:
        expected_finding_count[finding.ELECAUDITSID] += 1

    # Count the declared findings
    for audit in audits:
        declared_finding_count[audit.ELECAUDITSID] = string_to_int(audit.FINDINGSCOUNT)

    # Check for discrepancies in findings count
    if (
        len(expected_finding_count) != len(declared_finding_count)
        or sum(expected_finding_count.values()) != sum(declared_finding_count.values())
        or declared_finding_count != expected_finding_count
    ):
        is_incorrect_findings_count_found = True

    # Track invalid audit records if discrepancies are found
    if is_incorrect_findings_count_found:
        for audit in audits:
            elec_audits_id = audit.ELECAUDITSID
            expected_count = expected_finding_count[elec_audits_id]
            track_invalid_records(
                [
                    ("ELECAUDITSID", elec_audits_id),
                    ("FINDINGSCOUNT", audit.FINDINGSCOUNT),
                ],
                "findings_count",
                str(expected_count),
                invalid_audit_records,
            )

        InvalidRecord.append_validations_to_skip("check_findings_count_consistency")
        InvalidRecord.append_invalid_migration_tag(
            INVALID_MIGRATION_TAGS.INCORRECT_FINDINGS_COUNT,
        )
        InvalidRecord.append_invalid_federal_awards_records(invalid_audit_records)


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
    # See Transformation Method Change Recording at the top of this file.
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
    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_empty_program_total_found:
        InspectionRecord.append_federal_awards_changes(change_records)


def xform_missing_cluster_total(
    audits,
    cluster_names,
    other_cluster_names,
    state_cluster_names,
):
    """Calculates missing cluster total for each award. This method is now deprecated."""
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
    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_empty_cluster_total_found:
        InspectionRecord.append_federal_awards_changes(change_records)


def xform_missing_cluster_total_v2(
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
    invalid_records = []
    is_empty_cluster_total_found = False
    is_incorrect_cluster_total_found = False

    for idx, (name, audit) in enumerate(zip(cluster_names, audits)):
        cluster_total = string_to_string(audit.CLUSTERTOTAL)
        if not cluster_total:
            is_empty_cluster_total_found = True
        else:
            cluster_total = string_to_int(cluster_total)

        gsa_cluster_total = expected_cluster_total(
            idx=idx,
            name=name,
            uniform_other_cluster_names=uniform_other_cluster_names,
            uniform_state_cluster_names=uniform_state_cluster_names,
            state_cluster_names=state_cluster_names,
            cluster_names=cluster_names,
            amounts_expended=amounts_expended,
        )

        if cluster_total != "" and cluster_total != gsa_cluster_total:
            is_incorrect_cluster_total_found = True
        else:
            cluster_total = gsa_cluster_total

        track_invalid_records(
            [
                ("CLUSTERTOTAL", cluster_total),
                ("CLUSTERNAME", audit.CLUSTERNAME),
                ("STATECLUSTERNAME", audit.STATECLUSTERNAME),
                ("OTHERCLUSTERNAME", audit.OTHERCLUSTERNAME),
            ],
            "cluster_total",
            gsa_cluster_total,
            invalid_records,
        )
        track_transformations(
            "CLUSTERTOTAL",
            audit.CLUSTERTOTAL,
            "cluster_total",
            cluster_total,
            ["xform_missing_cluster_total_v2"],
            change_records,
        )

        audit.CLUSTERTOTAL = str(cluster_total)

    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_empty_cluster_total_found:
        InspectionRecord.append_federal_awards_changes(change_records)

    if invalid_records and is_incorrect_cluster_total_found:
        InvalidRecord.append_invalid_federal_awards_records(invalid_records)
        InvalidRecord.append_validations_to_skip("cluster_total_is_correct")
        InvalidRecord.append_invalid_migration_tag(
            INVALID_MIGRATION_TAGS.INCORRECT_CLUSTER_TOTAL,
        )


def xform_is_passthrough_award(audits):
    """
    Replaces missing PASSTHROUGHAWARD with GSA_MIGRATION.
    """
    change_records = []
    is_empty_award_found = False

    for audit in audits:
        award = string_to_string(audit.PASSTHROUGHAWARD)

        if not award:
            is_empty_award_found = True
            award = settings.GSA_MIGRATION

        track_transformations(
            "PASSTHROUGHAWARD",
            audit.PASSTHROUGHAWARD,
            "is_passthrough_award",
            award,
            "xform_is_passthrough_award",
            change_records,
        )

        audit.PASSTHROUGHAWARD = award

    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_empty_award_found:
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


def xform_program_name(audits):
    """Default missing program_name to GSA_MIGRATION"""
    change_records = []
    is_empty_program_name_found = False

    for audit in audits:
        program_name = string_to_string(audit.FEDERALPROGRAMNAME)
        if not program_name:
            is_empty_program_name_found = True
            program_name = settings.GSA_MIGRATION

        track_transformations(
            "FEDERALPROGRAMNAME",
            audit.FEDERALPROGRAMNAME,
            "federal_program_name",
            program_name,
            ["xform_program_name"],
            change_records,
        )

        audit.FEDERALPROGRAMNAME = program_name

    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_empty_program_name_found:
        InspectionRecord.append_federal_awards_changes(change_records)


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


def xform_replace_missing_prefix(audits):
    """Replaces missing ALN prefixes with the corresponding value in CFDA"""
    change_records = []
    is_empty_prefix_found = False
    for audit in audits:
        prefix = string_to_string(audit.CFDA_PREFIX)
        if not prefix:
            is_empty_prefix_found = True
            prefix = string_to_string(audit.CFDA).split(".")[0]

        track_transformations(
            "CFDA_PREFIX",
            audit.CFDA_PREFIX,
            "federal_agency_prefix",
            prefix,
            ["xform_replace_missing_prefix"],
            change_records,
        )

        audit.CFDA_PREFIX = prefix

    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_empty_prefix_found:
        InspectionRecord.append_federal_awards_changes(change_records)


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
    Ensures that the number of passthrough IDs and the number of passthrough names match.
    If there are more names than IDs (or more IDs than names), fills in the missing IDs (respectively, missing names) with a placeholder.
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
        elif length_difference < 0:
            patch = [settings.GSA_MIGRATION for _ in range(-length_difference)]
            if name == "":
                patch.append(settings.GSA_MIGRATION)
                names[idx] = "|".join(patch)
            else:
                passthrough_names.extend(patch)
                names[idx] = "|".join(passthrough_names)
        elif name and not id:
            ids[idx] = settings.GSA_MIGRATION

        elif id and not name:
            names[idx] = settings.GSA_MIGRATION

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
        if direct in {"N", settings.GSA_MIGRATION} and name == "":
            passthrough_names[index] = settings.GSA_MIGRATION
        if direct == "N" and id == "":
            passthrough_ids[index] = settings.GSA_MIGRATION
    return (passthrough_names, passthrough_ids)


def xform_replace_invalid_direct_award_flag(audits, passthrough_names):
    """Replaces invalid DIRECT award flags with the default value settings.GSA_MIGRATION."""
    is_directs = []
    change_records = []
    is_invalid_direct_flag_found = False
    for audit, name in zip(audits, passthrough_names):
        is_direct = string_to_string(audit.DIRECT)
        if is_direct == "Y" and name:
            is_invalid_direct_flag_found = True
            track_transformations(
                "DIRECT",
                audit.DIRECT,
                "is_direct",
                settings.GSA_MIGRATION,
                ["xform_replace_invalid_direct_award_flag"],
                change_records,
            )
            is_directs.append(settings.GSA_MIGRATION)
        else:
            track_transformations(
                "DIRECT",
                is_direct,
                "is_direct",
                is_direct,
                ["xform_replace_invalid_direct_award_flag"],
                change_records,
            )
            is_directs.append(is_direct)
    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_invalid_direct_flag_found:
        InspectionRecord.append_federal_awards_changes(change_records)

    return is_directs


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


def xform_sanitize_additional_award_identification(audits, identifications):
    """Sanitize the input to ensure it does not start with ="" and end with " which might be interpreted as a formula in Excel."""

    change_records = []
    new_identifications = []
    has_modified_identification = False
    for audit, identification in zip(audits, identifications):
        if (
            identification
            and identification.startswith('=""')
            and identification.endswith('"')
        ):
            new_identification = identification[3:-1]
            has_modified_identification = True
        else:
            new_identification = identification
        new_identifications.append(new_identification)

        track_transformations(
            "AWARDIDENTIFICATION",
            audit.AWARDIDENTIFICATION,
            "additional_award_identification",
            new_identification,
            ["xform_sanitize_additional_award_identification"],
            change_records,
        )
    # See Transformation Method Change Recording at the top of this file.
    if change_records and has_modified_identification:
        InspectionRecord.append_federal_awards_changes(change_records)

    return new_identifications


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

        if passthrough_award == settings.GSA_MIGRATION:
            if not amount or amount == "0":
                passthrough_amounts.append("")
            else:
                passthrough_amounts.append(amount)
        elif passthrough_award == "Y":
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


def xform_cluster_names(audits):
    """
    Replaces "OTHER CLUSTER" with the settings.OTHER_CLUSTER value.
    """

    change_records = []
    is_other_cluster_found = False
    for audit in audits:
        cluster_name = string_to_string(audit.CLUSTERNAME)
        if cluster_name and cluster_name.upper() == "OTHER CLUSTER":
            is_other_cluster_found = True
            cluster_name = settings.OTHER_CLUSTER
        track_transformations(
            "CLUSTERNAME",
            audit.CLUSTERNAME,
            "cluster_name",
            cluster_name,
            ["xform_cluster_names"],
            change_records,
        )
        audit.CLUSTERNAME = cluster_name
    # See Transformation Method Change Recording at the top of this file.
    if change_records and is_other_cluster_found:
        InspectionRecord.append_federal_awards_changes(change_records)
    return audits


def track_invalid_federal_program_total(audits, cfda_key_values):
    """
    Tracks invalid federal program totals.
    """
    federal_program_total_values = get_range_values("PROGRAMTOTAL", audits, None, int)
    amount_expended_values = get_range_values("AMOUNT", audits, None, int)
    invalid_records = []
    amount_expended_values = get_range_values("AMOUNT", audits, None, int)
    has_invalid_federal_program_total = False
    # Validating each federal_program_total
    for idx, key in enumerate(cfda_key_values):
        # Compute the sum for current cfda_key
        computed_sum = sum(
            [
                amount
                for k, amount in zip(cfda_key_values, amount_expended_values)
                if k == key
            ]
        )
        if computed_sum != federal_program_total_values[idx]:
            has_invalid_federal_program_total = True

        census_data_tuples = [
            ("PROGRAMTOTAL", federal_program_total_values[idx]),
            ("AMOUNT", amount_expended_values[idx]),
            ("CFDA", key),
        ]
        track_invalid_records(
            census_data_tuples,
            "federal_program_total",
            computed_sum,
            invalid_records,
        )

    if has_invalid_federal_program_total and invalid_records:
        InvalidRecord.append_invalid_federal_awards_records(invalid_records)
        InvalidRecord.append_validations_to_skip("federal_program_total_is_correct")
        InvalidRecord.append_invalid_migration_tag(
            INVALID_MIGRATION_TAGS.INVALID_FEDERAL_PROGRAM_TOTAL
        )


def xform_replace_required_values_with_gsa_migration_when_empty(audits):
    """Replace empty fields with GSA_MIGRATION."""
    fields_to_check = [
        ("LOANS", "is_loan"),
        ("DIRECT", "is_direct"),
    ]

    for in_db, in_dissem in fields_to_check:
        _replace_empty_field(audits, in_db, in_dissem)


def _replace_empty_field(audits, name_in_db, name_in_dissem):
    """Replace empty fields with GSA_MIGRATION."""
    change_records = []
    has_empty_field = False
    for audit in audits:
        current_value = getattr(audit, name_in_db)
        if not string_to_string(current_value):
            has_empty_field = True
            setattr(audit, name_in_db, settings.GSA_MIGRATION)

        track_transformations(
            name_in_db,
            current_value,
            name_in_dissem,
            settings.GSA_MIGRATION,
            ["xform_replace_required_values_with_gsa_migration_when_empty"],
            change_records,
        )

    if change_records and has_empty_field:
        InspectionRecord.append_federal_awards_changes(change_records)


def generate_federal_awards(audit_header, outfile):
    """
    Generates a federal awards workbook for all awards associated with a given audit header.
    """
    logger.info(
        f"--- generate federal awards {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )

    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.FEDERAL_AWARDS])
    uei = xform_retrieve_uei(audit_header.UEI)
    set_workbook_uei(wb, uei)
    audits = get_audits(audit_header.DBKEY, audit_header.AUDITYEAR)
    audits = xform_cluster_names(audits)

    (
        cluster_names,
        other_cluster_names,
        state_cluster_names,
    ) = xform_constructs_cluster_names(audits)

    xform_missing_cluster_total_v2(
        audits, cluster_names, other_cluster_names, state_cluster_names
    )
    xform_missing_program_total(audits)

    xform_missing_findings_count(audits)
    xform_missing_amount_expended(audits)
    xform_program_name(audits)
    xform_is_passthrough_award(audits)
    xform_missing_major_program(audits)
    track_invalid_number_of_audit_findings(audits, audit_header)
    xform_replace_required_values_with_gsa_migration_when_empty(audits)
    xform_replace_missing_prefix(audits)
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

    is_directs = xform_replace_invalid_direct_award_flag(audits, passthrough_names)
    set_range(wb, "is_direct", is_directs)

    # The award numbers!
    set_range(
        wb,
        "award_reference",
        [f"AWARD-{n + 1:04}" for n in range(len(audits))],
    )

    # passthrough amount
    passthrough_amounts = xform_populate_default_passthrough_amount(audits)
    set_range(wb, "subrecipient_amount", passthrough_amounts)

    # additional award identification
    additional_award_identifications = (
        xform_populate_default_award_identification_values(audits)
    )
    updated_awward_identifications = xform_sanitize_additional_award_identification(
        audits, additional_award_identifications
    )
    set_range(
        wb,
        "additional_award_identification",
        updated_awward_identifications,
    )

    # loan balance at audit period end
    loan_balances = xform_populate_default_loan_balance(audits)
    set_range(
        wb,
        "loan_balance_at_audit_period_end",
        loan_balances,
    )
    track_invalid_federal_program_total(audits, full_cfdas)
    # Total amount expended must be calculated and inserted
    total = 0
    for audit in audits:
        total += int(audit.AMOUNT)
    set_range(wb, "total_amount_expended", [str(total)])
    wb.save(outfile)

    return wb
