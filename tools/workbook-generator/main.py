from collections import defaultdict
from collections import namedtuple as NT
from pathlib import Path
from playhouse.shortcuts import model_to_dict, dict_to_model
import os

import argparse
import json
import openpyxl as pyxl

from data.models import (
    Cfda,
    Gen,
    Passthrough,
    Findings
)

parser = argparse.ArgumentParser()

# Award Reference (Read Only)
# Federal Agency Prefix
# ALN (CFDA) Three Digit Extension
# Additional Award Identification
# Federal Program Name
# Amount Expended
# Cluster Name
# If State Cluster, Enter State Cluster Name
# If Other Cluster, Enter Other Cluster Name
# Federal Program Total
# Cluster Total
# Loan / Loan Guarantee
# If yes (Loan/Loan Guarantee, End of Audit Period Outstanding Loan Balance)
# Direct Award
# If no (Direct Award), Name of Passthrough Entity
# If no (Direct Award), Identifying Number Assigned by the Pass-through Entity, if assigned
# Federal Award Passed Through to Subrecipients
# If yes (Passed Through), Amount Passed Through to Subrecipients	Major Program (MP)
# If yes (MP), Type of Audit Report
# Number of Audit Findings


def set_single_cell_range(wb, range_name, value):
    the_range = wb.defined_names[range_name]
    # The above returns a generator. Turn it to a list, and grab
    # the first element of the list. Now, this *tuple* contains a
    # sheet name and a cell reference... which you need to get rid
    # of the '$' to use.
    # https://itecnote.com/tecnote/python-using-excel-named-ranges-in-python-with-openpyxl/
    tup = list(the_range.destinations)[0]
    sheet_title = tup[0]
    cell_ref = tup[1].replace('$', '')
    ws = wb[sheet_title]
    ws[cell_ref] = value


def col_to_ndx(col):
    return ord(col) - 65 + 1


def set_range(wb, range_name, values, default=None, type=str):
    the_range = wb.defined_names[range_name]
    dest = list(the_range.destinations)[0]
    sheet_title = dest[0]
    ws = wb[sheet_title]

    start_cell = dest[1].replace('$', '').split(':')[0]
    col = col_to_ndx(start_cell[0])
    start_row = int(start_cell[1])

    for ndx, v in enumerate(values):
        row = ndx+start_row
        if v:
            print(f'{range_name} c[{row}][{col}] <- {v} len({len(v)}) {default}')
            ws.cell(row=row, column=col, value=type(v))
            if len(v) == 0 and default is not None:
                print('Applying default')
                ws.cell(row=row, column=col, value=type(default))
        if not v:
            if default is not None:
               ws.cell(row=row, column=col, value=type(default))
            else:
                ws.cell(row=row, column=col, value='')
        else:
            # Leave it blank if we have no default passed in
            pass


def show(v):
    print(json.dumps(model_to_dict(v)))
    return v


FieldMap = NT('FieldMap', 'in_sheet in_db default type')


# Award Reference	
# Audit Finding Reference Number	
# Type(s) of Compliance Requirement(s)	
# Modified Opinion	
# Other Matters	
# Material Weakness	
# Significant Deficiency	
# Other Findings	
# Questioned Costs	
# Repeat Findings from Prior Year	
# If Repeat Finding, provide Prior Year Audit Finding Reference Number(s)	
# Is Findings Combination Valid? (Read Only)

def generate_findings(dbkey):
    print("--- generate_findings ---")
    wb = pyxl.load_workbook('templates/findings-uniform-guidance-template.xlsx')
    mappings = [
       FieldMap('compliance_requirement', 'typerequirement', None, str), 
       FieldMap('reference_number', 'findingsrefnums', None, str),
       FieldMap('modified_opinion', 'modifiedopinion', None, str), 
       FieldMap('other_matters', 'othernoncompliance', None, str), 
       FieldMap('material_weakness', 'materialweakness', None, str), 
       FieldMap('significant_deficiency', 'significantdeficiency', None, str), 
       FieldMap('other_findings', 'otherfindings', None, str),
       FieldMap('questioned_costs', 'qcosts', None, str),
       FieldMap('repeat_prior_reference', 'repeatfinding', None, str), 
       FieldMap('prior_references', 'priorfindingrefnums', None, str), 
       # is_valid is computed in the workbook
    ]

    g = Gen.select().where(Gen.dbkey == dbkey).get()
    set_single_cell_range(wb, 'auditee_uei', g.uei)
    # Mapping the award numbers will require ELECAUDITIDs.
    cfdas = Cfda.select(Cfda.elecauditsid).where(Cfda.dbkey == g.dbkey)
    findings = Findings.select().where(Findings.dbkey == g.dbkey)
    
    # For each of them, I need to generate an elec -> award mapping.
    e2a = {}
    for ndx, cfda in enumerate(cfdas):
        e2a[cfda.elecauditsid] = f'AWARD-{ndx+1:04d}'

    award_references = []
    for find in findings:
        award_references.append(e2a[find.elecauditsid])
    set_range(wb, 'award_reference', award_references)

    # Map all the simple ones
    for m in mappings:
        set_range(wb, 
                  m.in_sheet,
                  map(lambda v: model_to_dict(v)[m.in_db], findings),
                  m.default, 
                  m.type)
    wb.save(os.path.join('output', dbkey, f'findings-{dbkey}.xlsx'))


def generate_federal_awards(dbkey):
    print("--- generate_federal_awards ---")
    wb = pyxl.load_workbook('templates/federal-awards-expended-template.xlsx')
    # In sheet : in DB
    mappings = [
        FieldMap('program_name', 'federalprogramname', None, str),
        FieldMap('additional_award_identification', 'awardidentification', None, str),
        FieldMap('cluster_name', 'clustername', None, str),
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
        FieldMap('number_of_audit_findings', 'findings', 0, int)
    ]

    # FIXME: Why only one?
    g = Gen.select().where(Gen.dbkey ==  dbkey).get()
    set_single_cell_range(wb, 'auditee_uei', g.uei)
    cfdas = Cfda.select().where(Cfda.dbkey == g.dbkey)

    # Map all the simple ones
    for m in mappings:
        set_range(wb, 
                  m.in_sheet,
                  map(lambda v: model_to_dict(v)[m.in_db], cfdas),
                  m.default, 
                  m.type)

    # Map things with transformations
    set_range(wb, 'federal_agency_prefix', map(
        lambda v: (v.cfda).split('.')[0], cfdas))
    set_range(wb, 'three_digit_extension', map(
        lambda v: (v.cfda).split('.')[1], cfdas))

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
            # print(f'Looking up {cfda.dbkey}, {cfda.elecauditsid} <- {json.dumps(model_to_dict(pnq))}')
        except Exception as e:
            passthrough_names.append('')
            passthrough_ids.append('')
    set_range(wb, 'passthrough_name', passthrough_names)
    set_range(wb, 'passthrough_identifying_number', passthrough_ids)

    try:
        os.mkdir(os.path.join('output', dbkey))
    except Exception as e:
        pass

    wb.save(os.path.join('output', dbkey, f'federal-awards-{dbkey}.xlsx'))


def main():
    generate_federal_awards(args.dbkey)
    generate_findings(args.dbkey)

if __name__ == '__main__':
    parser.add_argument('--dbkey', type=str, required=True)
    args = parser.parse_args()
    main()
