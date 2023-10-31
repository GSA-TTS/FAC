from .excel_creation import (
    FieldMap,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
)

from .excel_creation import insert_version_and_sheet_name
from audit.models import SingleAuditChecklist
from c2g.models import (
    ELECAUDITHEADER as Gen,
    ELECAUDITS as Cfda,
    ELECAUDITFINDINGS as Findings,
)


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
        "typerequirement".upper(),
        "type_requirement",
        "ABC",
        sorted_string,
    ),
    FieldMap(
        "reference_number", "findingrefnums".upper(), "reference_number", None, str
    ),
    FieldMap(
        "modified_opinion", "modifiedopinion".upper(), "is_modified_opinion", None, str
    ),
    FieldMap(
        "other_matters", "othernoncompliance".upper(), "is_other_matters", None, str
    ),
    FieldMap(
        "material_weakness",
        "materialweakness".upper(),
        "is_material_weakness",
        None,
        str,
    ),
    FieldMap(
        "significant_deficiency",
        "significantdeficiency".upper(),
        "is_significant_deficiency",
        None,
        str,
    ),
    FieldMap("other_findings", "otherfindings".upper(), "is_other_findings", None, str),
    FieldMap("questioned_costs", "qcosts".upper(), "is_questioned_costs", None, str),
    FieldMap(
        "repeat_prior_reference",
        "repeatfinding".upper(),
        "is_repeat_finding",
        None,
        str,
    ),
    FieldMap(
        "prior_references",
        "priorfindingrefnums".upper(),
        "prior_finding_ref_numbers",
        "N/A",
        str,
    ),
    # FIXME: We have to calculate, and patch in, is_valid
    # is_valid is computed in the workbook
]


def generate_findings(sac: SingleAuditChecklist, dbkey, audit_year, outfile):
    logger.info(f"--- generate findings {dbkey} {audit_year} ---")

    wb = pyxl.load_workbook(templates["AuditFindings"])
    set_uei(sac, wb)
    insert_version_and_sheet_name(wb, "federal-awards-audit-findings-workbook")

    cfdas = Cfda.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    # For each of them, I need to generate an elec -> award mapping.
    e2a = {}
    cfda: Cfda
    for ndx, cfda in enumerate(cfdas):
        e2a[cfda.ELECAUDITSID] = f"AWARD-{ndx+1:04d}"

    # CFDAs have elecauditid (FK). Findings have elecauditfindingsid, which is unique.
    # The linkage here is that a given finding will have an elecauditid.
    # Multiple findings will have a given elecauditid. That's how to link them.
    findings = (
        Findings.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
        # Findings.select().where(Findings.dbkey == g.dbkey).order_by(Findings.index)
    )
    award_references = []
    finding: Findings
    for finding in findings:
        award_references.append(e2a[finding.ELECAUDITSID])

    map_simple_columns(wb, mappings, findings)
    set_range(wb, "award_reference", award_references)

    wb.save(outfile)

    table = generate_dissemination_test_table(
        sac, "findings", audit_year, dbkey, mappings, findings
    )
    for obj, ar in zip(table["rows"], award_references):
        obj["fields"].append("award_reference")
        obj["values"].append(ar)

    return (wb, table)
