from datetime import date
import json

from django.conf import settings

from c2g.models import ELECAUDITHEADER as Gen, ELECAUDITS as Cfda


def get_cpacpuntry(country: str):
    if country.upper() in ["", "US", "USA"]:
        cpacountry = "USA"
    else:
        cpacountry = "non-USA"
    return cpacountry


def normalize_entity_type(entity_type: str):
    entity_type = entity_type.lower()
    if entity_type == "local government":
        entity_type = "local"
    if entity_type == "institution of higher education":
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


cfda_extra = {
    "cluster_names": [],
    "other_cluster_names": [],
}

valid_file = open(f"{settings.BASE_DIR}/schemas/source/base/ClusterNames.json")
valid_json = json.load(valid_file)
UNDEFINED_CLUSTER_NAME = "OTHER CLUSTER NOT LISTED ABOVE"


def normalize_cluster_name(cname: str):
    if not cname or len(cname) == 0:
        return "N/A"
    if cname not in valid_json["cluster_names"]:
        return UNDEFINED_CLUSTER_NAME
    return cname


def derive_other_cluster_name(raw_cname: str, normalized_cname: str):
    if normalized_cname == UNDEFINED_CLUSTER_NAME:
        return raw_cname
    return ""


def set_extra_cfda_attrinute(name, value):
    cfda_extra[name].append(value)


def get_extra_cfda_attrinutes(name):
    return cfda_extra[name]


def clean_gen(gen: Gen):
    gen.ENTITY_TYPE = normalize_entity_type(gen.ENTITY_TYPE)
    gen.CPACOUNTRY = get_cpacountry(gen.CPACOUNTRY)
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
