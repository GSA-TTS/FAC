from audit.fixtures.workbooks.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    set_single_cell_range,
    map_simple_columns,
    generate_dissemination_test_table,
)

from audit.fixtures.census_models.ay22 import (
    CensusGen22 as Gen,
    CensusNotes22 as Notes,
)

import openpyxl as pyxl
import re

import logging

logger = logging.getLogger(__name__)

mappings = [
    FieldMap("note_title", "title", None, str),
    FieldMap("note_content", "content", None, str),
]


def generate_notes_to_sefa(dbkey, outfile):
    logger.info(f"--- generate notes to sefa {dbkey}---")
    wb = pyxl.load_workbook(templates["SEFA"])

    g = set_uei(Gen, wb, dbkey)

    # The mapping is weird.
    # https://facdissem.census.gov/Documents/DataDownloadKey.xlsx
    # The TYPEID column determines which field in the form a given row corresponds to.
    # TYPEID=1 is the description of significant accounting policies.
    # TYPEID=2 is the De Minimis cost rate.
    # TYPEID=3 is for notes, which have sequence numbers... that must align somewhere.
    policies = (
        Notes.select().where((Notes.dbkey == g.dbkey) & (Notes.type_id == 1)).get()
    )
    rate = Notes.select().where((Notes.dbkey == g.dbkey) & (Notes.type_id == 2)).get()
    notes = (
        Notes.select()
        .where((Notes.dbkey == g.dbkey) & (Notes.type_id == 3))
        .order_by(Notes.seq_number)
    )

    # This looks like the right way to set the three required fields
    set_single_cell_range(wb, "accounting_policies", policies.content)
    # WARNING
    # This is being faked. We're askign a Y/N question in the collection.
    # Census just let them type some stuff. So, this is a rough
    # attempt to generate a Y/N value from the content.
    # This means the data is *not* true to what was intended, but
    # it *is* good enough for us to use for testing.
    is_used = "Huh"
    if (
        re.search("did not use", rate.content)
        or re.search("not to use", rate.content)
        or re.search("not use", rate.content)
        or re.search("not elected", rate.content)
    ):
        is_used = "N"
    elif re.search("used", rate.content):
        is_used = "Y"
    else:
        is_used = "Y&N"

    set_single_cell_range(wb, "is_minimis_rate_used", is_used)
    set_single_cell_range(wb, "rate_explained", rate.content)

    # Map the rest as notes.
    map_simple_columns(wb, mappings, notes)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "notes_to_sefa", dbkey, mappings, notes
    )
    table["singletons"]["accounting_policites"] = policies.content
    table["singletons"]["is_minimis_rate_used"] = is_used
    table["singletons"]["rate_explained"] = rate.content
    table["singletons"]["auditee_uei"] = g.uei
    return (wb, table)
