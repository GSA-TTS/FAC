from ..transforms.xform_string_to_string import (
    string_to_string,
)
from ..workbooklib.excel_creation_utils import (
    get_audits,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
    set_workbook_uei,
)
from ..base_field_maps import SheetFieldMap
from ..workbooklib.templates import sections_to_template_paths
from audit.fixtures.excel import FORM_SECTIONS
from ..models import ELECAUDITFINDINGS as Findings
import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


def sorted_string(s):
    s_sorted = "".join(sorted(s))
    # print(f's before: {s} after {s_sorted}')
    return s_sorted


def xform_prior_year_findings(value):
    """
    Transform the value of prior_references to N/A if empty."""
    trimmed_value = string_to_string(value)
    if trimmed_value == "":
        # FIXME - MSHD: This is a transformation and might require logging.
        # Why is this transformation needed? Because users were allowed to leave this empty
        # but we have decided to enforce that they enter N/A (starting in 2023).
        # Therefore, we need to transform the empty string to N/A, otherwise the new validation
        # rule will fail most of the migration.
        # logger.info(f"Prior year findings is empty. Setting to N/A.")
        new_value = "N/A"
    else:
        new_value = trimmed_value
    return new_value


mappings = [
    SheetFieldMap(
        "compliance_requirement",
        "TYPEREQUIREMENT",
        "type_requirement",
        None,
        # FIXME - MSHD: I removed sorted_string from here because it is a transformation and
        # we want to apply transformation in a more controlled way (not by default - except when required).
        str,
    ),
    SheetFieldMap("reference_number", "FINDINGREFNUMS", "reference_number", None, str),
    SheetFieldMap(
        "modified_opinion", "MODIFIEDOPINION", "is_modified_opinion", None, str
    ),
    SheetFieldMap("other_matters", "OTHERNONCOMPLIANCE", "is_other_matters", None, str),
    SheetFieldMap(
        "material_weakness", "MATERIALWEAKNESS", "is_material_weakness", None, str
    ),
    SheetFieldMap(
        "significant_deficiency",
        "SIGNIFICANTDEFICIENCY",
        "is_significant_deficiency",
        None,
        str,
    ),
    SheetFieldMap("other_findings", "OTHERFINDINGS", "is_other_findings", None, str),
    SheetFieldMap("questioned_costs", "QCOSTS", "is_questioned_costs", None, str),
    SheetFieldMap(
        "repeat_prior_reference", "REPEATFINDING", "is_repeat_finding", None, str
    ),
    SheetFieldMap(
        "prior_references",
        "PRIORFINDINGREFNUMS",
        "prior_finding_ref_numbers",
        None,
        xform_prior_year_findings,
    ),
]


def _get_findings_grid(findings_list):
    # The original copy of allowed_combos is in audit/intakelib/checks/check_findings_grid_validation.py
    allowed_combos = {
        "YNNNN",
        "YNYNN",
        "YNNYN",
        "NYNNN",
        "NYYNN",
        "NYNYN",
        "NNYNN",
        "NNNYN",
        "NNNNY",
    }

    attributes = [
        "MODIFIEDOPINION",
        "OTHERNONCOMPLIANCE",
        "MATERIALWEAKNESS",
        "SIGNIFICANTDEFICIENCY",
        "OTHERFINDINGS",
    ]

    return [
        "Y"
        if "".join((getattr(finding, attr, "") or "").strip() for attr in attributes)
        in allowed_combos
        else "N"
        for finding in findings_list
    ]


def _get_findings(dbkey, year):
    # CFDAs aka ELECAUDITS (or Audits) have elecauditid (FK). Findings have elecauditfindingsid, which is unique.
    # The linkage here is that a given finding will have an elecauditid.
    # Multiple findings will have a given elecauditid. That's how to link them.
    return Findings.objects.filter(DBKEY=dbkey, AUDITYEAR=year).order_by(
        "ELECAUDITFINDINGSID"
    )


def generate_findings(audit_header, outfile):
    """
    Generates a federal awards audit findings workbook for all findings associated with a given audit header.
    """
    logger.info(
        f"--- generate findings {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )

    wb = pyxl.load_workbook(
        sections_to_template_paths[FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE]
    )
    set_workbook_uei(wb, audit_header.UEI)
    audits = get_audits(audit_header.DBKEY, audit_header.AUDITYEAR)
    # For each of them, I need to generate an elec -> award mapping.
    e2a = {}
    for index, audit in enumerate(audits):
        e2a[audit.ELECAUDITSID] = f"AWARD-{index+1:04d}"

    findings = _get_findings(audit_header.DBKEY, audit_header.AUDITYEAR)

    award_references = []
    for find in findings:
        award_references.append(e2a[find.ELECAUDITSID])

    map_simple_columns(wb, mappings, findings)
    set_range(wb, "award_reference", award_references)

    grid = _get_findings_grid(findings)
    # We need a magic "is_valid" column, which is computed in the workbook.
    set_range(wb, "is_valid", grid, conversion_fun=str)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        audit_header, "findings", mappings, findings
    )
    for obj, ar in zip(table["rows"], award_references):
        obj["fields"].append("award_reference")
        obj["values"].append(ar)

    return (wb, table)
