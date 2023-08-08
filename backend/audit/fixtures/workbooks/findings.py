from audit.fixtures.workbooks.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    set_single_cell_range,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
)

from audit.fixtures.census_models.ay22 import (
    CensusCfda22 as Cfda,
    CensusFindings22 as Findings,
    CensusGen22 as Gen,
)

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

def sorted_string(s):
    return ''.join(sorted(s))

mappings = [
    FieldMap("compliance_requirement", "typerequirement", None, sorted_string),
    FieldMap("reference_number", "findingsrefnums", None, str),
    FieldMap("modified_opinion", "modifiedopinion", None, str),
    FieldMap("other_matters", "othernoncompliance", None, str),
    FieldMap("material_weakness", "materialweakness", None, str),
    FieldMap("significant_deficiency", "significantdeficiency", None, str),
    FieldMap("other_findings", "otherfindings", None, str),
    FieldMap("questioned_costs", "qcosts", None, str),
    FieldMap("repeat_prior_reference", "repeatfinding", None, str),
    FieldMap("prior_references", "priorfindingrefnums", None, str),
    # FIXME: We have to calculate, and patch in, is_valid
    # is_valid is computed in the workbook
]


def generate_findings(dbkey, outfile):
    logger.info(f"--- generate findings {dbkey} ---")
    wb = pyxl.load_workbook(templates["AuditFindings"])
    g = set_uei(Gen, wb, dbkey)
    cfdas = Cfda.select(Cfda.elecauditsid).where(Cfda.dbkey == g.dbkey)
    findings = Findings.select().where(Findings.dbkey == g.dbkey)

    map_simple_columns(wb, mappings, findings)

    # For each of them, I need to generate an elec -> award mapping.
    e2a = {}
    award_references = []
    if (cfdas != None) and (findings != None):
        for ndx, cfda in enumerate(cfdas):
            if cfda:
                e2a[cfda.elecauditsid] = f"AWARD-{ndx+1:04d}"

        if len(e2a) != 0:
            for find in findings:
                if find:
                    award_references.append(e2a[find.elecauditsid])

            if len(award_references) != 0:
                set_range(wb, "award_reference", award_references)

    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "findings", dbkey, mappings, findings
    )
    for obj, ar in zip(table["rows"], award_references):
        obj["fields"].append("award_reference")
        obj["values"].append(ar)

    return (wb, table)
