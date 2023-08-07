from audit.management.commands.workbooks.base import (
    FieldMap,
    templates,
    set_uei,
    set_single_cell_range,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range
)

from audit.management.commands.census_models.ay22 import  (
    CensusCfda22 as Cfda,
    CensusPassthrough22 as Passthrough,
    CensusGen22 as Gen
)

import openpyxl as pyxl

import logging
logger = logging.getLogger(__name__)

mappings = [
    FieldMap('program_name', 'federalprogramname', None, str),
    FieldMap('additional_award_identification', 'awardidentification', None, str),
    FieldMap('cluster_name', 'clustername', "N/A", str),
    FieldMap('state_cluster_name', 'stateclustername', None, str),
    FieldMap('other_cluster_name', 'otherclustername', None, str),
    FieldMap('federal_program_total', 'programtotal', 0, int),
    FieldMap('cluster_total', 'clustertotal', 0, float),
    FieldMap('is_guaranteed', 'loans', None, str),
    FieldMap('loan_balance_at_audit_period_end', 'loanbalance', None, float),
    FieldMap('is_direct', 'direct', None, str),
    FieldMap('is_passed', 'passthroughaward', None, str),
    FieldMap('subrecipient_amount', 'passthroughamount', None, float),
    FieldMap('is_major', 'majorprogram', None, str),
    FieldMap('audit_report_type', 'typereport_mp', None, str),
    FieldMap('number_of_audit_findings', 'findings', 0, int),
    FieldMap('amount_expended', 'amount', 0, int),
    FieldMap('federal_program_total', 'programtotal', 0, int)
]

def generate_federal_awards(dbkey, outfile):
    logger.info(f"--- generate federal awards {dbkey}---")
    wb = pyxl.load_workbook(templates["FederalAwards"])
    # In sheet : in DB

    g = set_uei(Gen, wb, dbkey)
    cfdas = Cfda.select().where(Cfda.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, cfdas)
    
    # Map things with transformations
    prefixes = map(lambda v: (v.cfda).split('.')[0], cfdas)
    extensions = map(lambda v: (v.cfda).split('.')[1], cfdas)
    set_range(wb, 'federal_agency_prefix', prefixes)
    set_range(wb, 'three_digit_extension', extensions)

    # We have to hop through several tables to build a list 
    # of passthrough names. Note that anything without a passthrough
    # needs to be represented in the list as an empty string.
    passthrough_names = []
    passthrough_ids = []
    for cfda in cfdas:
        try:
            pnq = (Passthrough
                   .select()
                   .where((Passthrough.dbkey == cfda.dbkey) &
                          (Passthrough.elecauditsid == cfda.elecauditsid))).get()
            passthrough_names.append(pnq.passthroughname)
            passthrough_ids.append(pnq.passthroughid)
        except Exception as e:
            passthrough_names.append('')
            passthrough_ids.append('')
    set_range(wb, 'passthrough_name', passthrough_names)
    set_range(wb, 'passthrough_identifying_number', passthrough_ids)

    # The award numbers!
    set_range(wb, 'award_reference', [f"AWARD-{n+1:04}" for n in range(len(passthrough_names))])

    # Total amount expended must be calculated and inserted
    total = 0
    for cfda in cfdas:
        total += int(cfda.amount)
    set_single_cell_range(wb, 'total_amount_expended', total)

    wb.save(outfile)

    table = generate_dissemination_test_table(Gen, 'federal_awards', dbkey, mappings, cfdas)
    award_counter = 1
    # prefix
    for obj, pfix, ext in zip(table['rows'], prefixes, extensions):
        obj['fields'].append('federal_agency_prefix')
        obj['values'].append(pfix)
        obj['fields'].append('three_digit_extension')
        obj['values'].append(ext)
        # Sneak in the award number here
        obj['fields'].append('award_reference')
        obj['values'].append(f"AWARD-{award_counter:04}")
        award_counter += 1
    # names, ids
    for obj, name, id in zip(table['rows'], passthrough_names, passthrough_ids):
        obj['fields'].append('passthrough_name')
        obj['values'].append(name)
        obj['fields'].append('passthrough_identifying_number')
        obj['values'].append(id)
    table['singletons']['auditee_uei'] = g.uei
    table['singletons']['total_amount_expended'] = total

    return (wb, table)
