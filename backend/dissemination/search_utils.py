import logging
import re
from enum import Enum
from collections import namedtuple as NT

from django.db.models import Q, Func
from django.forms import BooleanField

from audit.models.constants import FINDINGS_FIELD_TO_BITMASK, FINDINGS_BITMASK
from dissemination.searchlib.search_constants import text_input_delimiters

logger = logging.getLogger(__name__)

# TODO: Clean-up
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

class JSONBitwiseOr(Func):
    function = 'jsonb_bitwise_or'
    arity = 4
    output_field = BooleanField()

def _search_names(params):
    names_list = params.get(SEARCH_FIELDS.NAMES)
    # TODO: Confirm
    name_fields = [
        # "auditee_city",
        "general_information__auditee_contact_name",
        "auditee_certification__auditee_name",
        "general_information__auditee_contact_name__auditee_email",
        "general_information__auditee_name",
        "general_information__auditor_contact_name",
        "auditor_certification__auditor_signature__auditor_name",
        "general_information__auditor_email",
        "general_information__auditor_firm_name",
    ]

    names_match = Q()

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

    # Now, for each field (e.g. "auditee_contact_name")
    # build up an AND over the terms. We want something where all of the
    # terms appear.
    # Then, do an OR over all of the fields. If that combo appears in
    # any of the fields, we want to return it.
    for field in name_fields:
        field_q = Q()
        for name in flattened:
            field_q.add(Q(**{f"audit__{field}__icontains": name}), Q.AND)
        names_match.add(field_q, Q.OR)

    # Now, "college berea" and "university state ohio" return
    # the appropriate terms. It is also significantly faster than what
    # we had before.
    return names_match

def _search_uei_ein(params):
    uei_ein = params.get(SEARCH_FIELDS.UEI_EIN)
    return Q(audit__general_information__auditee_ein__in=uei_ein) | \
            Q(audit__general_information__auditee_uei__in=uei_ein) | \
            Q(audit__additional_eins__contains=uei_ein) | \
            Q(audit__additional_ueis__contains=uei_ein)

def _search_alns(params):
    full_alns = _get_full_alns(params)
    agency_numbers = _get_agency_numbers(params)

    if not (full_alns or agency_numbers):
        return Q()

    query = Q()
    if agency_numbers:
        # Build a filter for the agency numbers. E.g. given 93 and 45
        for an in agency_numbers:
            query |= \
                Q(audit__federal_awards__awards__contains=[{"program": {"federal_agency_prefix" : an.prefix }}])

    if full_alns:
        for full_aln in full_alns:
            query |= Q(audit__federal_awards__awards__contains=[{"program": {"federal_agency_prefix" : full_aln.prefix }}]) & \
                              Q(audit__federal_awards__awards__contains=[{"program": {"three_digit_extension":full_aln.program}}])

    return query

def _search_cog_or_oversight(params):
    agency_name = params.get("agency_name", None)
    cog_or_oversight = params.get("cog_or_oversight", None)
    if cog_or_oversight.lower() in ["", "either"]:
        if agency_name:
            return Q(
                Q(audit__cognizant_agency__in=[agency_name])
                | Q(audit__oversight_agency__in=[agency_name])
            )
        else:
            # Every submission should have a value for either cog or over, so
            # nothing to do here
            return Q()
    elif cog_or_oversight.lower() == "cog":
        if agency_name:
            return Q(audit__cognizant_agency__in=[agency_name])
        else:
            # Submissions that have any cog
            return Q(audit__cognizant_agency__isnull=False)
    elif cog_or_oversight.lower() == "oversight":
        if agency_name:
            return Q(audit__oversight_agency__in=[agency_name])
        else:
            # Submissions that have any over
            return Q(audit__oversight_agency__isnull=False)

def _search_federal_program_name(params):
    query = Q()
    names = params.get("federal_program_name")
    for name in names:
        sub_query = Q()
        rsplit = re.compile("|".join(text_input_delimiters)).split

        for sub in [s.strip() for s in rsplit(name)]:
            sub_query.add(Q(audit__program_names__icontains=sub), Q.AND)

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
    # TODO: Figure out how to get the query to work on the generated field
    # where findings_summary & findings_mask > 0
    return Q()

def _search_direct_funding(params):
    q = Q()
    direct_funding_fields = params.get("direct_funding")
    for field in direct_funding_fields:
        match field:
            case "direct_funding":
                q |= Q(audit__federal_awards__awards__contains=[{"direct_or_indirect_award": {"is_direct":"Y"}}])
            case "passthrough_funding":
                q |= Q(audit__federal_awards__awards__contains=[{"direct_or_indirect_award": {"is_direct":"N"}}])
            case _:
                pass
    return q

def _search_major_program(params):
    q = Q()
    major_program_fields = params.get("major_program")
    if "True" in major_program_fields:
        q |= Q(audit__federal_awards__awards__contains=[{"program": {"is_major": "Y"}}])
    elif "False" in major_program_fields:
        q |= Q(audit__federal_awards__awards__contains=[{"program": {"is_major": "N"}}])
    return q

def _search_passthrough_name(params):
    q = Q()
    passthrough_names = params.get("passthrough_name")
    for term in passthrough_names:
        q_sub = Q()
        for sub in term.split():
            q_sub.add(Q(audit__passthrough__contains=[{"passthrough_name": sub}]), Q.AND)
        q.add(q_sub, Q.OR)
    return q

def _search_type_requirement(params):
    q = Q()
    type_requirements = params.get("type_requirement")
    for tr in type_requirements:
        q |= Q(audit__findings_uniform_guidance__contains=[{"program": { "compliance_requirement": tr}}])

    return q

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
                # The [wrapping] is so the tuple goes into the set as a tuple.
                # Otherwise, the individual elements go in unpaired.
                # split_alns.update([tuple(split_aln)])
                split_alns.update([ALN(split_aln[0], split_aln[1])])
    return split_alns

# TODO: Update to use generated fields
SEARCH_QUERIES = {
    SEARCH_FIELDS.AUDIT_YEARS: lambda params : Q(audit_year__in=params.get(SEARCH_FIELDS.AUDIT_YEARS.value)),
    SEARCH_FIELDS.AUDITEE_STATE: lambda params : Q(auditee_state__in=[params.get(SEARCH_FIELDS.AUDITEE_STATE.value)]),
    SEARCH_FIELDS.NAMES: _search_names,
    SEARCH_FIELDS.UEI_EIN: lambda params : _search_uei_ein,
    SEARCH_FIELDS.START_DATE: lambda params : Q(fac_accepted_date__date__gte=params.get(SEARCH_FIELDS.START_DATE.value)),
    SEARCH_FIELDS.END_DATE: lambda params : Q(fac_accepted_date__date__lte=params.get(SEARCH_FIELDS.END_DATE.value)),
    SEARCH_FIELDS.FY_END_MONTH: lambda params : Q(fy_end_month=params.get(SEARCH_FIELDS.FY_END_MONTH.value)),
    SEARCH_FIELDS.ENTITY_TYPE: lambda params: Q(organization_type__in=params.get(SEARCH_FIELDS.ENTITY_TYPE.value)),
    SEARCH_FIELDS.REPORT_ID: lambda params : Q(report_id=params.get(SEARCH_FIELDS.REPORT_ID.value)),
    # Advanced Search
    SEARCH_FIELDS.ALNS: _search_alns,
    SEARCH_FIELDS.COG_OVERSIGHT: _search_cog_or_oversight,
    SEARCH_FIELDS.FEDERAL_PROGRAM_NAME: _search_federal_program_name,
    SEARCH_FIELDS.FINDINGS: _search_findings,
    SEARCH_FIELDS.DIRECT_FUNDING: _search_direct_funding,
    SEARCH_FIELDS.MAJOR_PROGRAM: _search_major_program,
    SEARCH_FIELDS.PASSTHROUGH_NAME: _search_passthrough_name,
    SEARCH_FIELDS.TYPE_REQUIREMENT: _search_type_requirement,
}

## TODO: Fields to Index
# audit__audit_year
# audit__general_information__auditee_state
# audit__fac_accepted_date\
# audit__fy_end_month
# audit__general_information__user_provided_organization_type
# report_id
# general_information__auditee_contact_name,
# auditee_certification__auditee_name,
# general_information__auditee_contact_name__auditee_email,
# general_information__auditee_name,
# general_information__auditor_contact_name,
# auditor_certification__auditor_signature__auditor_name,
# general_information__auditor_email,
# general_information__auditor_firm_name
# audit__general_information__auditee_ein
# audit__general_information__auditee_uei
# audit__additional_eins
# audit__additional_ueis
# audit__federal_awards__awards__program__federal_agency_prefix
# audit__federal_awards__awards__program__is_major
# audit__federal_awards__awards__direct_or_indirect_award__is_direct
# audit__oversight_agency
# audit__cognizant_agency
# audit_program_names
