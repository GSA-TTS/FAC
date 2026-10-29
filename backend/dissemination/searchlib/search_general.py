import time
from math import ceil
import logging
from django.db.models import Q
from dissemination.models import AdditionalEin, AdditionalUei

logger = logging.getLogger(__name__)


def search_general(base_model, model_type, params=None):
    params = params or dict()
    # Time general reduction
    t0 = time.time()

    ##############
    # Initialize query.
    # r_base = base_model.objects.all()

    # grab only the columns we need as a QuerySet of Dictionaries
    if model_type == "general":
        r_base = base_model.objects.values(
            "id",
            "report_id",
            "entity_type",
            "audit_year",
            "auditee_certify_name",
            "auditee_contact_name",
            "auditee_ein",
            "auditee_email",
            "auditee_name",
            "auditee_uei",
            "auditee_state",
            "auditor_certify_name",
            "auditor_contact_name",
            "auditor_email",
            "auditor_firm_name",
            "resubmission_status",
            "cognizant_agency",
            "oversight_agency",
            "fac_accepted_date",
            "fy_end_date",
            "fy_start_date",
            "is_additional_ueis",
            "is_public",
            "resubmission_status",
            "resubmission_version",
        )
    else:
        r_base = base_model.objects.values(
            "id",
            "report_id",
            "aln",
            "entity_type",
            "audit_year",
            "auditee_certify_name",
            "auditee_contact_name",
            "auditee_ein",
            "auditee_email",
            "auditee_name",
            "auditee_uei",
            "auditee_state",
            "auditor_certify_name",
            "auditor_contact_name",
            "auditor_email",
            "auditor_firm_name",
            "resubmission_status",
            "cognizant_agency",
            "oversight_agency",
            "is_material_weakness",
            "is_modified_opinion",
            "is_other_findings",
            "is_other_matters",
            "is_questioned_costs",
            "is_repeat_finding",
            "is_significant_deficiency",
            "fac_accepted_date",
            "fy_end_date",
            "fy_start_date",
            "type_requirement",
            "passthrough_name",
            "is_direct",
            "is_major",
            "is_public",
            "federal_award_extension",
            "federal_agency_prefix",
            "federal_program_name",
            "is_additional_ueis",
            "resubmission_status",
            "resubmission_version",
        )

    ##############
    # Audit years
    # query.add(_get_audit_years_match_query(audit_years), Q.AND)
    q_audit_year = _get_audit_years_match_query(params.get("audit_years", None))
    r_audit_year = r_base.filter(q_audit_year)

    ##############
    # State
    q_state = _get_auditee_state_match_query(params.get("auditee_state", None))
    r_state = r_base.filter(q_state)

    ##############
    # Names
    q_names = _get_names_match_query(params.get("names", None))
    r_names = r_base.filter(q_names)

    ##############
    # UEI/EIN
    q_uei = _get_uei_or_eins_match_query(params.get("uei_or_eins", None))
    r_uei = r_base.filter(q_uei)

    ##############
    # Start/end dates
    start = params.get("start_date", None)
    end = params.get("end_date", None)

    # Unflip the dates if they're backwards
    if start and end and start > end:
        start = params.get("end_date", None)
        end = params.get("start_date", None)

    q_start_date = _get_start_date_match_query(start)
    r_start_date = r_base.filter(q_start_date)
    q_end_date = _get_end_date_match_query(end)
    r_end_date = r_base.filter(q_end_date)

    ##############
    # Fiscal year end month
    q_fy_end_month = _get_fy_end_month_match_query(params.get("fy_end_month", None))
    r_fy_end_month = r_base.filter(q_fy_end_month)

    ##############
    # Entity type
    q_entity_type = _get_entity_type_match_query(params.get("entity_type", None))
    r_entity_type = r_base.filter(q_entity_type)

    ##############
    # Report ID
    q_report_id = _get_report_id_match_query(params.get("report_id", None))
    r_report_id = r_base.filter(q_report_id)

    ##############
    # Intersection
    # Intersection on result sets is an &.
    results = (
        r_audit_year
        & r_state
        & r_names
        & r_uei
        & r_start_date
        & r_end_date
        & r_fy_end_month
        & r_entity_type
        & r_report_id
    )

    t1 = time.time()
    report_timing("search_general", params, t0, t1)
    return results


def report_timing(tag, params, start, end):
    readable = int(ceil((end - start) * 1000))
    logger.info(f"SEARCH_TIMING {hex(id(params))[8:]} {tag} {readable}ms")


def _get_uei_or_eins_match_query(uei_or_eins):
    if not uei_or_eins:
        return Q()

    r_uei = (
        AdditionalEin.objects.filter(additional_ein__in=uei_or_eins)
        .values_list("report_id")
        .distinct()
    )
    r_ein = (
        AdditionalUei.objects.filter(additional_uei__in=uei_or_eins)
        .values_list("report_id")
        .distinct()
    )
    uei_or_ein_match = Q(
        Q(auditee_ein__in=uei_or_eins)
        | Q(auditee_uei__in=uei_or_eins)
        | Q(report_id__in=r_ein)
        | Q(report_id__in=r_uei)
    )
    return uei_or_ein_match


def _get_start_date_match_query(start_date):
    if not start_date:
        return Q()

    return Q(fac_accepted_date__gte=start_date)


def _get_end_date_match_query(end_date):
    if not end_date:
        return Q()

    return Q(fac_accepted_date__lte=end_date)


def _get_audit_years_match_query(audit_years):
    if not audit_years:
        return Q()

    return Q(audit_year__in=audit_years)


def _get_auditee_state_match_query(auditee_state):
    if not auditee_state:
        return Q()

    return Q(auditee_state__in=[auditee_state])


def _get_names_match_query(names_list):
    """
    Given a list of (potential) names, return the query object that searches auditee and firm names.
    """
    if not names_list:
        return Q()

    name_fields = [
        # "auditee_city",
        "auditee_contact_name",
        "auditee_certify_name",
        "auditee_email",
        "auditee_name",
        # "auditee_state",
        # "auditor_city",
        "auditor_contact_name",
        "auditor_certify_name",
        "auditor_email",
        "auditor_firm_name",
        # "auditor_state",
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
            field_q.add(Q(**{f"{field}__icontains": name}), Q.AND)
        names_match.add(field_q, Q.OR)

    # Now, "college berea" and "university state ohio" return
    # the appropriate terms. It is also significantly faster than what
    # we had before.

    return names_match


def _get_fy_end_month_match_query(fy_end_month):
    if not fy_end_month:
        return Q()

    return Q(fy_end_date__month=fy_end_month)


def _get_entity_type_match_query(entity_types):
    if not entity_types:
        return Q()

    return Q(entity_type__in=entity_types)


def _get_report_id_match_query(report_ids):
    if not report_ids:
        return Q()

    return Q(report_id__in=report_ids)
