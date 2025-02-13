import logging
import re
from enum import Enum
from collections import namedtuple as NT

from django.db.models import Q, F

from audit.models.constants import FINDINGS_FIELD_TO_BITMASK, FINDINGS_BITMASK
from dissemination.searchlib.search_constants import text_input_delimiters

logger = logging.getLogger(__name__)

# TODO:
#  1) Verify all queries are working correctly. Double check findings and bitmasking.
#  2) Clean-up: Split all the search helpers into separate files?
class SEARCH_FIELDS(Enum):
    AUDIT_YEARS = "audit_years"
    AUDITEE_STATE = "auditee_state"
    NAMES = "names"
    UEI_EIN = "uei_or_eins"
    START_DATE = "start_date"
    END_DATE = "end_date"
    FY_END_MONTH = "fy_end_month"
    ENTITY_TYPE = "entity_type"
    REPORT_ID = "report_id"
    ALNS = "alns"
    COG_OVERSIGHT = "cog_or_oversight"
    FEDERAL_PROGRAM_NAME = "federal_program_name"
    FINDINGS = "findings"
    DIRECT_FUNDING = "direct_funding"
    MAJOR_PROGRAM = "major_program"
    PASSTHROUGH_NAME = "passthrough_name"
    TYPE_REQUIREMENT = "type_requirement"

def _search_names(params):
    names_list = params.get(SEARCH_FIELDS.NAMES.value)

    # The search terms are coming in as a string in a list.
    # E.g. the search text "college berea" returns nothing,
    # when it should return entries for "Berea College". That is
    # because it comes in as
    # ["college berea"]
    #
    # This has to be flattened to a list of singleton terms.
    flattened = []
    for term in names_list:
        for sub in term.split():
            flattened.append(sub)

    query = Q()
    for name in flattened:
        query |= Q(search_names__icontains=name)
    return query if flattened else Q()

def _search_uei_ein(params):
    uei_eins = params.get(SEARCH_FIELDS.UEI_EIN.value)
    uei_ein_query = Q()
    uei_ein_query |= Q(auditee_ein__in=uei_eins) | \
                     Q(auditee_uei__in=uei_eins)

    for uei_ein in uei_eins:
        uei_ein_query |= Q(additional_eins__icontains=uei_ein) | \
                         Q(additional_ueis__icontains=uei_ein)

    return uei_ein_query if uei_eins else Q()

def _search_alns(params):
    full_alns = _get_full_alns(params)
    agency_numbers = _get_agency_numbers(params)

    if not (full_alns or agency_numbers):
        return Q()

    query = Q()
    if agency_numbers:
        # Build a filter for the agency numbers. E.g. given 93 and 45
        for agency_number in agency_numbers:
            query |= Q(agency_prefixes__icontains=agency_number.prefix)

    if full_alns:
        for full_aln in full_alns:
            query |= Q(agency_prefixes__icontains=full_aln.prefix) & \
                              Q(agency_extensions__icontains=full_aln.program)

    return query

def _search_cog_or_oversight(params):
    agency_name = params.get("agency_name", None)
    cog_or_oversight = params.get("cog_or_oversight", None)
    if cog_or_oversight.lower() in ["", "either"]:
        if agency_name:
            return Q(
                Q(cognizant_agency__in=[agency_name])
                | Q(oversight_agency__in=[agency_name])
            )
        else:
            # Every submission should have a value for either cog or over, so
            # nothing to do here
            return Q()
    elif cog_or_oversight.lower() == "cog":
        if agency_name:
            return Q(cognizant_agency__in=[agency_name])
        else:
            # Submissions that have any cog
            return Q(cognizant_agency__isnull=False)
    elif cog_or_oversight.lower() == "oversight":
        if agency_name:
            return Q(oversight_agency__in=[agency_name])
        else:
            # Submissions that have any over
            return Q(oversight_agency__isnull=False)

def _search_federal_program_name(params):
    query = Q()
    names = params.get("federal_program_name")
    for name in names:
        sub_query = Q()
        rsplit = re.compile("|".join(text_input_delimiters)).split

        for sub in [s.strip() for s in rsplit(name)]:
            sub_query.add(Q(program_names__icontains=sub), Q.AND)

        query.add(sub_query, Q.OR)
    return query

def _search_findings(params):
    findings_fields = params.get("findings")

    findings_mask = 0
    if "all_findings" in findings_fields:
        findings_mask = FINDINGS_BITMASK.ALL
    else:
        for mask in FINDINGS_FIELD_TO_BITMASK:
            if mask.search_param in findings_fields:
                findings_mask = findings_mask | mask.mask
    # where findings_summary & findings_mask > 0
    return Q(findings_summary__gt=0) & Q(findings_summary__lt=F('findings_summary').bitor(findings_mask)) if findings_mask else Q()

def _search_direct_funding(params):
    q = Q()
    direct_funding_fields = params.get("direct_funding")
    for field in direct_funding_fields:
        match field:
            case "direct_funding":
                q |= Q(has_direct_funding=True)
            case "passthrough_funding":
                q |= Q(has_indirect_funding=False)
            case _:
                pass
    return q

def _search_passthrough_name(params):
    q = Q()
    passthrough_names = params.get("passthrough_name")
    for term in passthrough_names:
        q_sub = Q()
        for sub in term.split():
            q_sub.add(Q(passthrough_names__icontains=sub), Q.AND)
        q.add(q_sub, Q.OR)
    return q

def _search_major_program(params):
    q = Q()
    major_program_fields = params.get("major_program")
    if "True" in major_program_fields:
        q |= Q(is_major_program=True)
    elif "False" in major_program_fields:
        q |= Q(is_major_program=False)
    return q

def _search_compliance_requirement(params):
    q = Q()
    crs = params.get("type_requirement")
    for cr in crs:
        q_sub = Q()
        for sub in cr.split():
            q_sub.add(Q(compliance_requirements__icontains=sub), Q.AND)
        q.add(q_sub, Q.OR)
    return q if crs else Q()

ALN = NT("ALN", "prefix, program")
def _get_agency_numbers(params):
    alns = params.get("alns", [])
    split_alns = set()
    for aln in alns:
        if len(aln) == 2:
            split_alns.update([ALN(aln, None)])
        else:
            pass
    return split_alns

def _get_full_alns(params):
    alns = params.get("alns", [])
    split_alns = set()
    for aln in alns:
        if len(aln) == 2:
            pass
        else:
            split_aln = aln.split(".")
            if len(split_aln) == 2:
                split_alns.update([ALN(split_aln[0], split_aln[1])])
    return split_alns

SEARCH_QUERIES = {
    SEARCH_FIELDS.AUDIT_YEARS: lambda params : Q(audit_year__in=params.get(SEARCH_FIELDS.AUDIT_YEARS.value)),
    SEARCH_FIELDS.AUDITEE_STATE: lambda params : Q(auditee_state__in=[params.get(SEARCH_FIELDS.AUDITEE_STATE.value)]),
    SEARCH_FIELDS.NAMES: _search_names,
    SEARCH_FIELDS.UEI_EIN: _search_uei_ein,
    SEARCH_FIELDS.START_DATE: lambda params : Q(fac_accepted_date__date__gte=params.get(SEARCH_FIELDS.START_DATE.value)),
    SEARCH_FIELDS.END_DATE: lambda params : Q(fac_accepted_date__date__lte=params.get(SEARCH_FIELDS.END_DATE.value)),
    SEARCH_FIELDS.FY_END_MONTH: lambda params : Q(fy_end_month=params.get(SEARCH_FIELDS.FY_END_MONTH.value)),
    SEARCH_FIELDS.ENTITY_TYPE: lambda params: Q(organization_type__in=params.get(SEARCH_FIELDS.ENTITY_TYPE.value)),
    SEARCH_FIELDS.REPORT_ID: lambda params : Q(report_id__in=params.get(SEARCH_FIELDS.REPORT_ID.value)),
    # Advanced Search
    SEARCH_FIELDS.ALNS: _search_alns,
    SEARCH_FIELDS.COG_OVERSIGHT: _search_cog_or_oversight,
    SEARCH_FIELDS.FEDERAL_PROGRAM_NAME: _search_federal_program_name,
    SEARCH_FIELDS.FINDINGS: _search_findings,
    SEARCH_FIELDS.DIRECT_FUNDING: _search_direct_funding,
    SEARCH_FIELDS.MAJOR_PROGRAM: _search_major_program,
    SEARCH_FIELDS.PASSTHROUGH_NAME: _search_passthrough_name,
    SEARCH_FIELDS.TYPE_REQUIREMENT: _search_compliance_requirement
}
