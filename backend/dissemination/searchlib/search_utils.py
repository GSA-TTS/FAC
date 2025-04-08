import logging
import textwrap

import time
from math import ceil

import newrelic.agent

from config.settings import AGENCY_NAMES
from dissemination.search import search as search_sac
from dissemination.searchlib.audit_search import search as search_audit

logger = logging.getLogger(__name__)


def _add_search_params_to_newrelic(search_parameters):
    is_advanced = search_parameters["advanced_search_flag"]
    singles = [
        "start_date",
        "end_date",
        "auditee_state",
    ]

    multis = [
        "uei_or_eins",
        "names",
    ]

    if is_advanced:
        singles.append("cog_or_oversight")
        multis.append("alns")

    newrelic.agent.add_custom_attributes(
        [(f"request.search.{k}", str(search_parameters[k])) for k in singles]
    )

    newrelic.agent.add_custom_attributes(
        [(f"request.search.{k}", ",".join(search_parameters[k])) for k in multis]
    )

    newrelic.agent.add_custom_attribute(
        "request.search.audit_years",
        ",".join([str(ay) for ay in search_parameters["audit_years"]]),
    )


# TODO: Update Post SOC Launch -> Clean up to ignore basic/advanced
def run_search(form_data, is_soc=False):
    """
    Given cleaned form data, run the search.
    Returns the results QuerySet.
    """

    basic_parameters = {
        "audit_years": form_data["audit_year"],
        "auditee_state": form_data["auditee_state"],
        "end_date": form_data["end_date"],
        "entity_type": form_data["entity_type"],
        "fy_end_month": form_data["fy_end_month"],
        "names": form_data["entity_name"],
        "report_id": form_data["report_id"],
        "start_date": form_data["start_date"],
        "uei_or_eins": form_data["uei_or_ein"],
        "order_by": form_data["order_by"],
        "order_direction": form_data["order_direction"],
    }
    search_parameters = basic_parameters.copy()

    search_parameters["advanced_search_flag"] = form_data.get(
        "advanced_search_flag", True
    )
    if search_parameters["advanced_search_flag"]:
        advanced_parameters = {
            "agency_name": form_data["agency_name"],
            "alns": form_data["aln"],
            "cog_or_oversight": form_data["cog_or_oversight"],
            "direct_funding": form_data["direct_funding"],
            "federal_program_name": form_data["federal_program_name"],
            "findings": form_data["findings"],
            "major_program": form_data["major_program"],
            "passthrough_name": form_data["passthrough_name"],
            "type_requirement": form_data["type_requirement"],
        }
        search_parameters.update(advanced_parameters)

    _add_search_params_to_newrelic(search_parameters)

    return (
        _compare_searches(search_parameters)
        if is_soc
        else search_sac(search_parameters)
    )


# TODO: Update Post SOC Launch -> This can go
def populate_cog_over_name(results):
    agency_names = AGENCY_NAMES
    for result in results:
        if result.oversight_agency:
            agency_code = result.oversight_agency
            agency_name = agency_names.get(
                result.oversight_agency, result.oversight_agency
            )
            result.agency_name = "\n".join(
                textwrap.wrap(agency_code + " - " + agency_name + " (OVER)", width=20)
            )
        elif result.cognizant_agency:
            agency_code = result.cognizant_agency
            agency_name = agency_names.get(
                result.cognizant_agency, result.cognizant_agency
            )
            result.agency_name = "\n".join(
                textwrap.wrap(agency_code + " - " + agency_name + " (COG)", width=20)
            )
    return results


def audit_populate_cog_over_name(results):
    agency_names = AGENCY_NAMES
    for result in results:
        oversight_agency = result.audit.get("oversight_agency", "")
        cognizant_agency = result.audit.get("cognizant_agency", "")
        if oversight_agency:
            agency_code = oversight_agency
            agency_name = agency_names.get(oversight_agency, oversight_agency)
            result.audit.update(
                {
                    "agency_name": "\n".join(
                        textwrap.wrap(
                            agency_code + " - " + agency_name + " (OVER)", width=20
                        )
                    )
                }
            )
        elif cognizant_agency:
            agency_code = cognizant_agency
            agency_name = agency_names.get(cognizant_agency, cognizant_agency)
            result.audit.update(
                {
                    "agency_name": "\n".join(
                        textwrap.wrap(
                            agency_code + " - " + agency_name + " (COG)", width=20
                        )
                    )
                }
            )
    return results


# TODO: Update Post SOC Launch -> Pull out the extra search, logging.
def _compare_searches(search_parameters):
    audit_t0 = time.time()
    audit_results = search_audit(search_parameters)
    audit_count = audit_results.count()
    audit_t1 = time.time()

    sac_t0 = time.time()
    sac_results = search_sac(search_parameters)
    sac_results_count = sac_results.count()
    sca_t1 = time.time()

    audit_duration = int(ceil((audit_t1 - audit_t0) * 1000))
    sac_duration = int(ceil((sca_t1 - sac_t0) * 1000))

    logger.info("=========== SOT Search Data ======================")
    logger.info(f"Audit Count: {audit_count} Duration: {audit_duration} ms")
    logger.info(f"SAC Count: {sac_results_count} Duration: {sac_duration} ms")
    # Only log the query if mismatched
    if audit_count != sac_results_count:
        logger.error("!!!!!!! Search Mismatch !!!!!!!")
        logger.info(f"Audit Query: {audit_results.query}")
        logger.info(f"SAC Query: {sac_results.query}")
    logger.info("===================================================")

    mismatch = 0 if audit_count == sac_results_count else 1

    metrics = _generate_metrics(audit_duration, sac_duration, mismatch)
    newrelic.agent.record_custom_metrics(metrics)

    return audit_results


def _generate_metrics(audit_duration, sac_duration, mismatch):
    yield "Custom/Search/AuditSearchDuration", audit_duration
    yield "Custom/Search/AuditSearchDuration", sac_duration
    yield "Custom/Search/Mismatch", mismatch
    yield "Custom/Search/PerformanceDelta", sac_duration - audit_duration
