from ..change_record import (
    CensusRecord,
    InspectionRecord,
    GsaFacRecord,
)
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..transforms.xform_string_to_string import (
    string_to_string,
)
from ..workbooklib.excel_creation_utils import (
    get_audits,
    map_simple_columns,
    set_range,
    set_workbook_uei,
    sort_by_field,
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
    Transform the value of prior_references to N/A if empty.
    """
    # Transformation to be documented.
    trimmed_value = string_to_string(value)
    if not trimmed_value:
        # See ticket #2912
        return "N/A"

    return trimmed_value


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


def xform_construct_award_references(audits, findings):
    """Construct award references for findings."""
    # Transformation recorded.
    e2a = {}
    for index, audit in enumerate(audits):
        e2a[audit.ELECAUDITSID] = f"AWARD-{index+1:04d}"
    award_references = []
    change_records = []
    for find in findings:
        award_references.append(e2a[find.ELECAUDITSID])
        # Tracking changes
        census_data = [CensusRecord("ELECAUDITSID", find.ELECAUDITSID).to_dict()]
        gsa_fac_data = GsaFacRecord("award_reference", e2a[find.ELECAUDITSID]).to_dict()
        transformation_functions = ["xform_construct_award_references"]
        change_records.append(
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": transformation_functions,
            }
        )
    if change_records:
        InspectionRecord.append_finding_changes(change_records)

    return award_references


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
    results = Findings.objects.filter(DBKEY=dbkey, AUDITYEAR=year)

    return sort_by_field(results, "ELECAUDITFINDINGSID")


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
    uei = xform_retrieve_uei(audit_header.UEI)
    set_workbook_uei(wb, uei)
    audits = get_audits(audit_header.DBKEY, audit_header.AUDITYEAR)
    findings = _get_findings(audit_header.DBKEY, audit_header.AUDITYEAR)
    award_references = xform_construct_award_references(audits, findings)

    map_simple_columns(wb, mappings, findings)
    set_range(wb, "award_reference", award_references)

    grid = _get_findings_grid(findings)
    # We need a magic "is_valid" column, which is computed in the workbook.
    set_range(wb, "is_valid", grid, conversion_fun=str)
    wb.save(outfile)

    return wb
