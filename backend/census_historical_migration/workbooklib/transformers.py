from datetime import date
import json

from django.conf import settings

from ..models import ELECAUDITHEADER as Gen, ELECAUDITS as Cfda


def get_cpacpuntry(country: str):
    if country.upper() in ["", "US", "USA"]:
        cpacountry = "USA"
    else:
        cpacountry = "non-USA"
    return cpacountry


def normalize_entity_type(entity_type: str):
    entity_type = entity_type.lower()
    if "local government" in entity_type:
        entity_type = "local"
    if "institution of higher education" in entity_type:
        entity_type = "higher-ed"
    return entity_type


def normalize_zip(zip):
    strzip = str(zip)
    if len(strzip) == 9:
        return f"{strzip[0:5]}-{strzip[5:9]}"
    return strzip


def normalize_number(number: str):
    if number in ["N/A", "", None]:
        return "0"
    if _is_positive(number):
        return number
    return "0"


def _is_positive(s):
    try:
        value = int(s)
        return value >= 0
    except ValueError:
        return False


def str_to_date(cd: str):
    # example 12/31/2022 00:00:00
    if "/" in cd:
        year = int(cd.split("/")[2][:4])
        month = int(cd.split("/")[0])
        day = int(cd.split("/")[1])
        return date(year, month, day)

    # example 2022-12-31
    elements = cd.split("-")
    year = int(elements[0])
    month = int(elements[1])
    day = int(elements[2])
    return date(year, month, day)


def format_date(dt: str):
    return str_to_date(dt).strftime("%Y-%m-%d")


def make_report_id(audit_year, fy_end_date, dbkey):
    dt = str_to_date(fy_end_date)
    return f"{audit_year}-{dt.month:02}-TSTDAT-{dbkey.zfill(10)}"


cfda_extra: dict = {
    "cluster_names": [],
    "other_cluster_names": [],
    "prefixes": [],
    "extensions": [],
}

valid_file = open(f"{settings.BASE_DIR}/schemas/source/base/ClusterNames.json")
valid_json = json.load(valid_file)
UNDEFINED_CLUSTER_NAME = "OTHER CLUSTER NOT LISTED ABOVE"


def normalize_cluster_name(cname: str):
    if not cname or len(cname) == 0:
        return ""
    if cname not in valid_json["cluster_names"]:
        return UNDEFINED_CLUSTER_NAME
    return cname


def normalize_addl_award_id(award_id: str, cfda_id: str, dbkey):
    if "u" in cfda_id.lower() or "rd" in cfda_id.lower():
        if not award_id or len(award_id) == 0:
            return f"ADDITIONAL AWARD INFO - DBKEY {dbkey}"
        return award_id
    return ""


def derive_other_cluster_name(raw_cname: str, normalized_cname: str):
    if normalized_cname == UNDEFINED_CLUSTER_NAME:
        return raw_cname
    return ""


def derive_prefix(code: str):
    return code.split(".")[0]


def derive_extension(code: str):
    # TODO
    #     extensions = map(
    #     lambda v: v
    #     if re.search("^(RD|RD[0-9]|[0-9]{3}[A-Za-z]{0,1}|U[0-9]{2})$", v)
    #     else "000",
    #     extensions,
    # )

    return code.split(".")[1]


def normalize_loan_balance(lb: str, is_loan: str):
    if is_loan == "Y":
        if lb is None:
            return "1"
        else:
            return lb
    return ""


def set_extra_cfda_attrinute(name, value):
    cfda_extra[name].append(value)


def get_extra_cfda_attrinutes(name):
    return cfda_extra[name]


def clean_gen(gen: Gen):
    gen.ENTITY_TYPE = normalize_entity_type(gen.ENTITY_TYPE)
    gen.CPACOUNTRY = get_cpacpuntry(gen.CPACOUNTRY)
    gen.UEI = gen.UEI or "BADBADBADBAD"
    gen.FYSTARTDATE = format_date(gen.FYSTARTDATE)
    gen.FYENDDATE = format_date(gen.FYENDDATE)


def clean_cfda(cfda: Cfda):
    cfda.LOANBALANCE = normalize_number(cfda.LOANBALANCE)
    cfda.AMOUNT = normalize_number(cfda.AMOUNT)
    cfda.FINDINGSCOUNT = normalize_number(cfda.FINDINGSCOUNT)
    cluster_name = normalize_cluster_name(cfda.CLUSTERNAME)
    set_extra_cfda_attrinute("cluster_names", cluster_name)
    other_cluster_name = derive_other_cluster_name(cfda.CLUSTERNAME, cluster_name)
    set_extra_cfda_attrinute("other_cluster_names", other_cluster_name)
    set_extra_cfda_attrinute("prefixes", derive_prefix(cfda.CFDA))
    set_extra_cfda_attrinute("extensions", derive_extension(cfda.CFDA))
    cfda.AWARDIDENTIFICATION = normalize_addl_award_id(
        cfda.AWARDIDENTIFICATION, cfda.CFDA, cfda.DBKEY
    )
    cfda.STATECLUSTERNAME = (
        cfda.STATECLUSTERNAME if "STATE CLUSTER" == cfda.CLUSTERNAME else ""
    )
    cfda.TYPEREPORT_MP = "" if cfda.MAJORPROGRAM == "N" else cfda.TYPEREPORT_MP
    cfda.LOANBALANCE = normalize_loan_balance(cfda.LOANBALANCE, cfda.LOANS)
