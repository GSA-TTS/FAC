from .excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    test_pfix,
)

from .excel_creation import insert_version_and_sheet_name
from c2g.models import (
    ELECAUDITHEADER as Gen,
    ELECAUDITFINDINGS as Findings,
    ELECFINDINGSTEXT as FTexts,
    ELECCAPTEXT as CapTexts,
)


import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


def generate_corrective_action_plan(sac, dbkey, audit_year, outfile):
    logger.info(f"--- generate corrective action plan {dbkey} {audit_year} ---")
    wb = pyxl.load_workbook(templates["CAP"])
    mappings = [
        FieldMap(
            "reference_number",
            "findingrefnums".upper(),
            "finding_ref_number",
            None,
            str,
        ),
        FieldMap(
            "planned_action", "text".upper(), WorkbookFieldInDissem, None, test_pfix(3)
        ),
        FieldMap(
            "contains_chart_or_table",
            "chartstables".upper(),
            WorkbookFieldInDissem,
            None,
            str,
        ),
    ]

    set_uei(sac, wb)
    insert_version_and_sheet_name(wb, "corrective-action-plan-workbook")

    captexts = CapTexts.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)

    map_simple_columns(wb, mappings, captexts)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        sac, "corrective_action_plans", audit_year, dbkey, mappings, captexts
    )
    table["singletons"]["auditee_uei"] = sac.auditee_uei

    return (wb, table)
