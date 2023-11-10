import openpyxl as pyxl
import json
import re

import logging
from django.conf import settings

from .excel_creation import (
    FieldMap,
    get_upper,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    set_single_cell_range,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
)

from .excel_creation import insert_version_and_sheet_name
from c2g.models import (
    ELECAUDITS as Cfda,
    ELECAUDITHEADER as Gen,
    ELECPASSTHROUGH as Passthrough,
)


logger = logging.getLogger(__name__)


def if_zero_empty(v):
    if int(v) == 0:
        return ""
    else:
        return int(v)


mappings = [
    FieldMap("program_name", "federalprogramname", "federal_program_name", None, str),
    FieldMap(
        "state_cluster_name", "stateclustername", WorkbookFieldInDissem, None, str
    ),
    FieldMap("federal_program_total", "programtotal", WorkbookFieldInDissem, 0, int),
    FieldMap("cluster_total", "clustertotal", WorkbookFieldInDissem, 0, int),
    FieldMap("is_guaranteed", "loans", "is_loan", None, str),
    FieldMap(
        "loan_balance_at_audit_period_end", "loanbalance", "loan_balance", None, int
    ),
    FieldMap("is_direct", "direct", WorkbookFieldInDissem, None, str),
    FieldMap("is_passed", "passthroughaward", "is_passthrough_award", None, str),
    FieldMap(
        "subrecipient_amount",
        "passthroughamount",
        "passthrough_amount",
        None,
        if_zero_empty,
    ),
    FieldMap("is_major", "majorprogram", WorkbookFieldInDissem, None, str),
    FieldMap("audit_report_type", "typereport_mp", "audit_report_type", None, str),
    FieldMap("number_of_audit_findings", "findingscount", "findings_count", 0, int),
    FieldMap("amount_expended", "amount", WorkbookFieldInDissem, 0, int),
]


mappings = get_upper(mappings)


def get_list_index(all, index):
    counter = 0
    for o in list(all):
        if o.index == index:
            return counter
        else:
            counter += 1
    return -1


def int_or_na(o):
    if o == "N/A":
        return o
    elif isinstance(o, int):
        return int(o)
    else:
        return "N/A"


def _generate_cluster_names(cfdas, valid_json):
    cluster_names = []
    other_cluster_names = []
    cfda: Cfda
    for cfda in cfdas:
        if cfda.CLUSTERNAME is None or len(cfda.CLUSTERNAME) == 0:
            cluster_names.append("N/A")
            other_cluster_names.append("")
        elif cfda.CLUSTERNAME in valid_json["cluster_names"]:
            cluster_names.append(cfda.CLUSTERNAME)
            other_cluster_names.append("")
        else:
            logger.debug(f"Cluster {cfda.CLUSTERNAME} not in the list. Replacing.")
            cluster_names.append("OTHER CLUSTER NOT LISTED ABOVE")
            other_cluster_names.append(f"{cfda.CLUSTERNAME}")
    print("JMM:", cluster_names, other_cluster_names)
    return (cluster_names, other_cluster_names)


def _fix_addl_award_identification(cfdas):
    addls = ["" for _ in list(range(0, len(cfdas)))]
    cfda: Cfda
    for i in range(len(cfdas)):
        cfda = cfdas[i]
        if cfda.CFDA and ("u" in cfda.CFDA.lower() or "rd" in cfda.CFDA.lower()):
            if cfda.AWARDIDENTIFICATION is None or len(cfda.AWARDIDENTIFICATION) < 1:
                addls[i] = f"ADDITIONAL AWARD INFO - DBKEY {dbkey}"
            else:
                addls[i] = cfda.AWARDIDENTIFICATION
    return addls


def _fix_pfixes(cfdas):
    # Map things with transformations
    prefixes = map(lambda v: (v.CFDA).split(".")[0], cfdas)
    # prefixes = map(lambda v: f'0{v}' if int(v) < 10 else v, prefixes)
    # Truncate any nastiness in the CFDA extensions to three characters.
    extensions = map(lambda v: ((v.CFDA).split(".")[1])[:3].upper(), cfdas)
    extensions = map(
        lambda v: v
        if re.search("^(RD|RD[0-9]|[0-9]{3}[A-Za-z]{0,1}|U[0-9]{2})$", v)
        else "000",
        extensions,
    )
    return (prefixes, extensions, map(lambda v: v.CFDA, cfdas))


def _fix_passthroughs(cfdas):
    passthrough_names = ["" for _ in list(range(0, len(cfdas)))]
    passthrough_ids = ["" for _ in list(range(0, len(cfdas)))]
    cfda: Cfda
    for i in range(len(cfdas)):
        cfda = cfdas[i]
        pnq = Passthrough()
        if cfda.DIRECT == "Y":
            pnq.PASSTHROUGHNAME = ""
            pnq.PASSTHROUGHID = ""
        if cfda.DIRECT == "N":
            try:
                pnq = Passthrough.objects.get(
                    AUDITYEAR=cfda.AUDITYEAR, DBKEY=cfda.DBKEY
                )
            except Exception as e:
                print(e)
                pnq.passthroughname = "EXCEPTIONAL PASSTHROUGH NAME"
                pnq.passthroughid = "EXCEPTIONAL PASSTHROUGH ID"

        name = pnq.PASSTHROUGHNAME or ""
        name = name.rstrip()
        if name == "" and cfda.DIRECT == "N":
            passthrough_names[i] = "NO PASSTHROUGH NAME PROVIDED"
        else:
            passthrough_names[i] = name

        _id = pnq.PASSTHROUGHID or ""
        _id = _id.rstrip()
        if _id == "" and cfda.DIRECT == "N":
            passthrough_ids[i] = "NO PASSTHROUGH ID PROVIDED"
        else:
            passthrough_ids[i] = _id

    return (passthrough_names, passthrough_ids)


def generate_federal_awards(gen: Gen, outfile):
    dbkey, audit_year = gen.DBKEY, gen.AUDITYEAR
    logger.info(f"--- generate federal awards {dbkey} {audit_year} ---")
    wb = pyxl.load_workbook(templates["FederalAwards"])
    # In sheet : in DB

    uei = set_uei(gen, wb)
    insert_version_and_sheet_name(wb, "federal-awards-workbook")

    cfdas = Cfda.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    map_simple_columns(wb, mappings, cfdas)

    # Patch the clusternames. They used to be allowed to enter anything
    # they wanted.
    valid_file = open(f"{settings.BASE_DIR}/schemas/source/base/ClusterNames.json")
    valid_json = json.load(valid_file)
    # This was removed from the CSV...
    valid_json["cluster_names"].append("STATE CLUSTER")

    (cluster_names, other_cluster_names) = _generate_cluster_names(cfdas, valid_json)
    set_range(wb, "cluster_name", cluster_names)
    set_range(wb, "other_cluster_name", other_cluster_names)

    # Fix the additional award identification. If they had a "U", we want
    # to see something in the addl. column.
    addls = _fix_addl_award_identification(cfdas)
    set_range(wb, "additional_award_identification", addls)

    (prefixes, extensions, full_cfdas) = _fix_pfixes(cfdas)
    set_range(wb, "federal_agency_prefix", prefixes)
    set_range(wb, "three_digit_extension", extensions)

    # We need a `cfda_key` as a magic column for the summation logic to work/be checked.
    set_range(wb, "cfda_key", full_cfdas, conversion_fun=str)

    (passthrough_names, passthrough_ids) = _fix_passthroughs(cfdas)
    set_range(wb, "passthrough_name", passthrough_names)
    set_range(wb, "passthrough_identifying_number", passthrough_ids)

    # The award numbers!
    set_range(
        wb,
        "award_reference",
        [f"AWARD-{n+1:04}" for n in range(len(cfdas))],
    )

    # Total amount expended must be calculated and inserted
    total = 0
    for cfda in cfdas:
        total += int(cfda.AMOUNT)
    set_single_cell_range(wb, "total_amount_expended", total)

    loansatend = list()
    for cfda in cfdas:
        if cfda.LOANS == "Y":
            if cfda.LOANBALANCE is None:
                # loansatend.append("N/A")
                loansatend.append(1)
            else:
                loansatend.append(cfda.LOANBALANCE)
        else:
            loansatend.append("")
    # set_range(wb, "loan_balance_at_audit_period_end", loansatend, type=int_or_na)
    set_range(wb, "loan_balance_at_audit_period_end", loansatend, conversion_fun=int)

    wb.save(outfile)

    table = generate_dissemination_test_table(gen, "federal_awards", mappings, cfdas)
    award_counter = 1
    # prefix
    for obj, pfix, ext, addl, cn, ocn in zip(
        table["rows"], prefixes, extensions, addls, cluster_names, other_cluster_names
    ):
        obj["fields"].append("federal_agency_prefix")
        obj["values"].append(pfix)
        obj["fields"].append("three_digit_extension")
        obj["values"].append(ext)
        # Sneak in the award number here
        obj["fields"].append("award_reference")
        obj["values"].append(f"AWARD-{award_counter:04}")
        obj["fields"].append("additional_award_identification")
        obj["values"].append(addl)
        obj["fields"].append("cluster_name")
        obj["values"].append(cn)
        obj["fields"].append("other_cluster_name")
        obj["fields"].append(ocn)
        award_counter += 1

    table["singletons"]["auditee_uei"] = uei
    table["singletons"]["total_amount_expended"] = total

    return (wb, table)
