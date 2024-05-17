from ..change_record import (
    InspectionRecord,
)
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..transforms.xform_string_to_string import string_to_string
from ..transforms.xform_uppercase_y_or_n import uppercase_y_or_n
from ..workbooklib.excel_creation_utils import (
    get_audits,
    map_simple_columns,
    set_range,
    set_workbook_uei,
    sort_by_field,
    track_transformations,
)
from ..base_field_maps import SheetFieldMap
from ..workbooklib.templates import sections_to_template_paths
from audit.fixtures.excel import FORM_SECTIONS
from ..models import ELECAUDITFINDINGS as Findings
import openpyxl as pyxl
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

# Transformation Method Change Recording
# For the purpose of recording changes, the transformation methods (i.e., xform_***)
# below track all records related to the federal_awards section that undergoes transformation and
# log these changes in a temporary array called `change_records`.
# However, we only save this data into the InspectionRecord table if at least one of the records has been
# modified by the transformation. If no records related to the given section
# were modified, then we do not save `change_records` into the InspectionRecord.


def xform_sort_compliance_requirement(findings):
    """Sorts and uppercases the compliance requirement string."""
    # Transformation to be documented
    for finding in findings:
        value = string_to_string(finding.TYPEREQUIREMENT).upper()
        finding.TYPEREQUIREMENT = "".join(sorted(value))


def xform_missing_compliance_requirement(findings):
    """Defaults missing compliance_requirement to GSA_MIGRATION."""
    change_records = []
    is_empty_compliance_requirement_found = False

    for finding in findings:
        compliance_requirement = string_to_string(finding.TYPEREQUIREMENT)
        if not compliance_requirement:
            is_empty_compliance_requirement_found = True
            compliance_requirement = settings.GSA_MIGRATION

        track_transformations(
            "TYPEREQUIREMENT",
            finding.TYPEREQUIREMENT,
            "type_requirement",
            compliance_requirement,
            ["xform_missing_compliance_requirement"],
            change_records,
        )

        finding.TYPEREQUIREMENT = compliance_requirement

    # See Transformation Method Change Recording comment at the top of this file
    if change_records and is_empty_compliance_requirement_found:
        InspectionRecord.append_finding_changes(change_records)


def xform_prior_year_findings(value):
    """
    Transform the value of prior_references to N/A if empty.
    """
    # Transformation to be documented
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
        "modified_opinion",
        "MODIFIEDOPINION",
        "is_modified_opinion",
        None,
        uppercase_y_or_n,
    ),
    SheetFieldMap(
        "other_matters",
        "OTHERNONCOMPLIANCE",
        "is_other_matters",
        None,
        uppercase_y_or_n,
    ),
    SheetFieldMap(
        "material_weakness",
        "MATERIALWEAKNESS",
        "is_material_weakness",
        None,
        uppercase_y_or_n,
    ),
    SheetFieldMap(
        "significant_deficiency",
        "SIGNIFICANTDEFICIENCY",
        "is_significant_deficiency",
        None,
        uppercase_y_or_n,
    ),
    SheetFieldMap(
        "other_findings", "OTHERFINDINGS", "is_other_findings", None, uppercase_y_or_n
    ),
    SheetFieldMap(
        "questioned_costs", "QCOSTS", "is_questioned_costs", None, uppercase_y_or_n
    ),
    SheetFieldMap(
        "repeat_prior_reference",
        "REPEATFINDING",
        "is_repeat_finding",
        None,
        uppercase_y_or_n,
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
        track_transformations(
            "ELECAUDITSID",
            find.ELECAUDITSID,
            "award_reference",
            e2a[find.ELECAUDITSID],
            ["xform_construct_award_references"],
            change_records,
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
        (
            "Y"
            if "".join(
                (getattr(finding, attr, "") or "").strip() for attr in attributes
            )
            in allowed_combos
            else "N"
        )
        for finding in findings_list
    ]


def get_findings(dbkey, year):
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
    findings = get_findings(audit_header.DBKEY, audit_header.AUDITYEAR)
    award_references = xform_construct_award_references(audits, findings)
    xform_sort_compliance_requirement(findings)
    xform_missing_compliance_requirement(findings)
    map_simple_columns(wb, mappings, findings)
    set_range(wb, "award_reference", award_references)

    grid = _get_findings_grid(findings)
    # We need a magic "is_valid" column, which is computed in the workbook.
    set_range(wb, "is_valid", grid, conversion_fun=str)
    wb.save(outfile)

    return wb
