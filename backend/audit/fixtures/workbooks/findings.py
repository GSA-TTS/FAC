from audit.fixtures.workbooks.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
)

from audit.fixtures.census_models.census import (
    CensusCfda22 as Cfda,
    CensusFindings22 as Findings,
    CensusGen22 as Gen,
)
from audit.fixtures.workbooks.excel_creation import insert_version_and_sheet_name
import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


def sorted_string(s):
    s_sorted = "".join(sorted(s))
    # print(f's before: {s} after {s_sorted}')
    return s_sorted


mappings = [
    FieldMap(
        "compliance_requirement",
        "typerequirement",
        "type_requirement",
        "ABC",
        sorted_string,
    ),
    FieldMap("reference_number", "findingsrefnums", "finding_ref_number", None, str),
    FieldMap("modified_opinion", "modifiedopinion", "is_modified_opinion", None, str),
    FieldMap(
        "other_matters", "othernoncompliance", "is_other_non_compliance", None, str
    ),
    FieldMap(
        "material_weakness", "materialweakness", "is_material_weakness", None, str
    ),
    FieldMap(
        "significant_deficiency",
        "significantdeficiency",
        "is_significant_deficiency",
        None,
        str,
    ),
    FieldMap("other_findings", "otherfindings", "is_other_findings", None, str),
    FieldMap("questioned_costs", "qcosts", "is_questioned_costs", None, str),
    FieldMap("repeat_prior_reference", "repeatfinding", "is_repeat_finding", None, str),
    FieldMap(
        "prior_references",
        "priorfindingrefnums",
        "prior_finding_ref_numbers",
        None,
        str,
    ),
    # FIXME: We have to calculate, and patch in, is_valid
    # is_valid is computed in the workbook
]


def generate_findings(dbkey, outfile):
    logger.info(f"--- generate findings {dbkey} ---")
    wb = pyxl.load_workbook(templates["AuditFindings"])
    g = set_uei(Gen, wb, dbkey)
    insert_version_and_sheet_name(wb, "federal-awards-audit-findings-workbook")

    cfdas = Cfda.select().where(Cfda.dbkey == g.dbkey).order_by(Cfda.index)
    # For each of them, I need to generate an elec -> award mapping.
    e2a = {}
    for ndx, cfda in enumerate(cfdas):
        e2a[cfda.elecauditsid] = f"AWARD-{ndx+1:04d}"

    # CFDAs have elecauditid (FK). Findings have elecauditfindingsid, which is unique.
    # The linkage here is that a given finding will have an elecauditid.
    # Multiple findings will have a given elecauditid. That's how to link them.
    findings = (
        Findings.select().where(Findings.dbkey == g.dbkey).order_by(Findings.index)
    )
    award_references = []
    for find in findings:
        award_references.append(e2a[find.elecauditsid])

    map_simple_columns(wb, mappings, findings)
    set_range(wb, "award_reference", award_references)

    wb.save(outfile)

    table = generate_dissemination_test_table(Gen, "findings", dbkey, mappings, findings)
    for obj, ar in zip(table["rows"], award_references):
        obj["fields"].append("award_reference")
        obj["values"].append(ar)

    return (wb, table)
