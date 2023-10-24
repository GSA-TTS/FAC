from dissemination.workbooklib.excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    set_single_cell_range,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
)

from dissemination.workbooklib.excel_creation import insert_version_and_sheet_name
from dissemination.workbooklib.census_models.census import dynamic_import

from config import settings

import openpyxl as pyxl
import json
import re

import logging

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


def _generate_cluster_names(Cfda, cfdas, valid_json):
    cluster_names = []
    other_cluster_names = []
    cfda: Cfda
    for cfda in cfdas:
        if cfda.clustername is None:
            cluster_names.append("N/A")
            other_cluster_names.append("")
        elif cfda.clustername in valid_json["cluster_names"]:
            cluster_names.append(cfda.clustername)
            other_cluster_names.append("")
        else:
            logger.debug(f"Cluster {cfda.clustername} not in the list. Replacing.")
            cluster_names.append("OTHER CLUSTER NOT LISTED ABOVE")
            other_cluster_names.append(f"{cfda.clustername}")
    return (cluster_names, other_cluster_names)


def _fix_addl_award_identification(Cfda, cfdas, dbkey):
    addls = ["" for x in list(range(0, len(cfdas)))]
    for cfda in (
        Cfda.select()
        .where(
            (Cfda.dbkey == dbkey)
            & (
                (Cfda.cfda % "%U%")
                | (Cfda.cfda % "%u%")
                | (Cfda.cfda % "%rd%")
                | (Cfda.cfda % "%RD%")
            )
        )
        .order_by(Cfda.index)
    ):
        if cfda.awardidentification is None or len(cfda.awardidentification) < 1:
            addls[
                get_list_index(cfdas, cfda.index)
            ] = f"ADDITIONAL AWARD INFO - DBKEY {dbkey}"
        else:
            addls[get_list_index(cfdas, cfda.index)] = cfda.awardidentification
    return addls


def _fix_pfixes(cfdas):
    # Map things with transformations
    prefixes = map(lambda v: (v.cfda).split(".")[0], cfdas)
    # prefixes = map(lambda v: f'0{v}' if int(v) < 10 else v, prefixes)
    # Truncate any nastiness in the CFDA extensions to three characters.
    extensions = map(lambda v: ((v.cfda).split(".")[1])[:3].upper(), cfdas)
    extensions = map(
        lambda v: v
        if re.search("^(RD|RD[0-9]|[0-9]{3}[A-Za-z]{0,1}|U[0-9]{2})$", v)
        else "000",
        extensions,
    )
    return (prefixes, extensions, map(lambda v: v.cfda, cfdas))


def _fix_passthroughs(Cfda, Passthrough, cfdas, dbkey):
    passthrough_names = ["" for x in list(range(0, len(cfdas)))]
    passthrough_ids = ["" for x in list(range(0, len(cfdas)))]
    ls = Cfda.select().where(Cfda.dbkey == dbkey).order_by(Cfda.index)
    cfda: Cfda
    for cfda in ls:
        pnq = Passthrough()
        if cfda.direct == "Y":
            pnq.passthroughname = ""
            pnq.passthroughid = ""
        if cfda.direct == "N":
            try:
                pnq = (
                    Passthrough.select().where(
                        (Passthrough.dbkey == cfda.dbkey)
                        & (Passthrough.elecauditsid == cfda.elecauditsid)
                    )
                ).get()
            except Exception as e:
                print(e)
                pnq.passthroughname = "EXCEPTIONAL PASSTHROUGH NAME"
                pnq.passthroughid = "EXCEPTIONAL PASSTHROUGH ID"

        name = pnq.passthroughname
        if name is None:
            name = ""
        name = name.rstrip()
        if name == "" and cfda.direct == "N":
            passthrough_names[
                get_list_index(cfdas, cfda.index)
            ] = "NO PASSTHROUGH NAME PROVIDED"
        else:
            passthrough_names[get_list_index(cfdas, cfda.index)] = name

        id = pnq.passthroughid
        if id is None:
            id = ""
        id = id.rstrip()
        if id == "" and cfda.direct == "N":
            passthrough_ids[
                get_list_index(cfdas, cfda.index)
            ] = "NO PASSTHROUGH ID PROVIDED"
        else:
            passthrough_ids[get_list_index(cfdas, cfda.index)] = pnq.passthroughid

    return (passthrough_names, passthrough_ids)


def generate_federal_awards(dbkey, year, outfile):
    logger.info(f"--- generate federal awards {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    Passthrough = dynamic_import("Passthrough", year)
    Cfda = dynamic_import("Cfda", year)
    wb = pyxl.load_workbook(templates["FederalAwards"])
    # In sheet : in DB

    g = set_uei(Gen, wb, dbkey)
    insert_version_and_sheet_name(wb, "federal-awards-workbook")

    cfdas = Cfda.select().where(Cfda.dbkey == dbkey).order_by(Cfda.index)
    map_simple_columns(wb, mappings, cfdas)

    # Patch the clusternames. They used to be allowed to enter anything
    # they wanted.
    valid_file = open(f"{settings.BASE_DIR}/schemas/source/base/ClusterNames.json")
    valid_json = json.load(valid_file)
    # This was removed from the CSV...
    valid_json["cluster_names"].append("STATE CLUSTER")

    (cluster_names, other_cluster_names) = _generate_cluster_names(
        Cfda, cfdas, valid_json
    )
    set_range(wb, "cluster_name", cluster_names)
    set_range(wb, "other_cluster_name", other_cluster_names)

    # Fix the additional award identification. If they had a "U", we want
    # to see something in the addl. column.
    addls = _fix_addl_award_identification(Cfda, cfdas, dbkey)
    set_range(wb, "additional_award_identification", addls)

    (prefixes, extensions, full_cfdas) = _fix_pfixes(cfdas)
    set_range(wb, "federal_agency_prefix", prefixes)
    set_range(wb, "three_digit_extension", extensions)

    # We need a `cfda_key` as a magic column for the summation logic to work/be checked.
    set_range(wb, "cfda_key", full_cfdas, conversion_fun=str)

    (passthrough_names, passthrough_ids) = _fix_passthroughs(
        Cfda, Passthrough, cfdas, dbkey
    )
    set_range(wb, "passthrough_name", passthrough_names)
    set_range(wb, "passthrough_identifying_number", passthrough_ids)

    # The award numbers!
    set_range(
        wb,
        "award_reference",
        [f"AWARD-{n+1:04}" for n in range(len(passthrough_names))],
    )

    # Total amount expended must be calculated and inserted
    total = 0
    for cfda in cfdas:
        total += int(cfda.amount)
    set_single_cell_range(wb, "total_amount_expended", total)

    loansatend = list()
    for ndx, cfda in enumerate(
        Cfda.select().where((Cfda.dbkey == dbkey)).order_by(Cfda.index)
    ):
        if cfda.loans == "Y":
            if cfda.loanbalance is None:
                # loansatend.append("N/A")
                loansatend.append(1)
            else:
                loansatend.append(cfda.loanbalance)
        else:
            loansatend.append("")
    # set_range(wb, "loan_balance_at_audit_period_end", loansatend, type=int_or_na)
    set_range(wb, "loan_balance_at_audit_period_end", loansatend, conversion_fun=int)

    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "federal_awards", dbkey, mappings, cfdas
    )
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

    table["singletons"]["auditee_uei"] = g.uei
    table["singletons"]["total_amount_expended"] = total

    return (wb, table)
