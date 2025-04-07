import json
import logging
import textwrap

import newrelic.agent

from config.settings import AGENCY_NAMES
from dissemination.searchlib.audit_search import search

logger = logging.getLogger(__name__)


def run_search(form_data):
    """
    Given cleaned form data, run the search.
    Returns the results QuerySet.
    """

    search_parameters = {
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

    _add_search_params_to_newrelic(search_parameters)

    return search(search_parameters)


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


def gather_errors(form):
    """
    Gather errors based on the form fields inputted by the user.
    """
    formatted_errors = []
    if form.errors:
        if not form.is_valid():
            errors = json.loads(form.errors.as_json())
            for error in reversed(errors):
                if "start_date" in error:
                    formatted_errors.append("The start date you entered is invalid.")
                if "end_date" in error:
                    formatted_errors.append("The end date you entered is invalid.")

    return formatted_errors


def _add_search_params_to_newrelic(search_parameters):

    singles = [
        "start_date",
        "end_date",
        "auditee_state",
    ]

    multis = [
        "uei_or_eins",
        "names",
    ]

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
