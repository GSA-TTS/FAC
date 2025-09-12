from requests import get
import os
from hashlib import sha1
import logging
from datetime import datetime
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.INFO)

field_name_ordered = {
    "general": [
        "agencies_with_prior_findings",
        "audit_period_covered",
        "audit_type",
        "audit_year",
        "auditee_address_line_1",
        "auditee_certified_date",
        "auditee_certify_name",
        "auditee_certify_title",
        "auditee_city",
        "auditee_contact_name",
        "auditee_contact_title",
        "auditee_ein",
        "auditee_email",
        "auditee_name",
        "auditee_phone",
        "auditee_state",
        "auditee_uei",
        "auditee_zip",
        "auditor_address_line_1",
        "auditor_certified_date",
        "auditor_certify_name",
        "auditor_certify_title",
        "auditor_city",
        "auditor_contact_name",
        "auditor_contact_title",
        "auditor_country",
        "auditor_ein",
        "auditor_email",
        "auditor_firm_name",
        "auditor_foreign_address",
        "auditor_phone",
        "auditor_state",
        "auditor_zip",
        "cognizant_agency",
        "data_source",
        "dollar_threshold",
        "entity_type",
        "fac_accepted_date",
        "fy_end_date",
        "fy_start_date",
        "gaap_results",
        "is_additional_ueis",
        "is_aicpa_audit_guide_included",
        "is_going_concern_included",
        "is_internal_control_deficiency_disclosed",
        "is_internal_control_material_weakness_disclosed",
        "is_low_risk_auditee",
        "is_material_noncompliance_disclosed",
        "is_public",
        "is_sp_framework_required",
        "number_months",
        "oversight_agency",
        "report_id",
        "sp_framework_basis",
        "sp_framework_opinions",
        "total_amount_expended",
        "type_audit_code",
        # 20250912 MCJ: Because of the off-by-one issues in timezones, it might be best
        # to leave these out of the hash until those issues are resolved. Or, figure out what is
        # going on that the hashing is happening before the timezone issue, because (somehow)
        # the hash is being computed before the data changes and hits the dissem tables.
        # "date_created",
        # "ready_for_certification_date",
        # "submitted_date",
    ],
    "federal_awards": [
        "report_id",
        "award_reference",
        "federal_agency_prefix",
        "federal_award_extension",
        "aln",
        "findings_count",
        "additional_award_identification",
        "federal_program_name",
        "amount_expended",
        "federal_program_total",
        "cluster_name",
        "state_cluster_name",
        "other_cluster_name",
        "cluster_total",
        "is_direct",
        "is_passthrough_award",
        "passthrough_amount",
        "is_major",
        "audit_report_type",
        "is_loan",
        "loan_balance",
    ],
    "findings": [
        "report_id",
        "federal_agency_prefix",
        "federal_award_extension",
        "aln",
        "award_reference",
        "reference_number",
        "type_requirement",
        "is_modified_opinion",
        "is_other_findings",
        "is_material_weakness",
        "is_significant_deficiency",
        "is_other_matters",
        "is_questioned_costs",
        "is_repeat_finding",
        "prior_finding_ref_numbers",
    ],
    "findings_text": [
        "id",
        "report_id",
        "finding_ref_number",
        "contains_chart_or_table",
        "finding_text",
    ],
    "notes_to_sefa": [
        "id",
        "report_id",
        "note_title",
        "accounting_policies",
        "rate_explained",
        "is_minimis_rate_used",
        "content",
        "contains_chart_or_table",
    ],
    "corrective_action_plans": [
        "report_id",
        "finding_ref_number",
        "planned_action",
        "contains_chart_or_table",
    ],
    "additional_eins": ["report_id", "additional_ein"],
    "additional_ueis": ["report_id", "additional_uei"],
    "passthrough": [
        "report_id",
        "award_reference",
        "passthrough_name",
        "passthrough_id",
    ],
    "secondary_auditors": [
        "report_id",
        "auditor_name",
        "auditor_ein",
        "address_street",
        "address_city",
        "address_state",
        "address_zipcode",
        "contact_name",
        "contact_title",
        "contact_email",
        "contact_phone",
    ],
}

from dateutil.parser import parse


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except Exception:
        return False


def convert_to_string(o):
    if isinstance(o, str) and len(o) == 10 and is_date(o):
        return f"{o}"
    if o is None:
        return ""
    else:
        return f"{o}"


# Ideally, this code would be *identical* to the code used inside of the FAC.
# It should be published, at first as part of an ADR.
def hash_dissemination_object(endpoint, d):
    # Given a hash, alpha sort the keys. We do this by taking
    # the object to a list of tuples, and then sorting
    # the resulting list on the first element of the tuple.
    #
    # See https://stackoverflow.com/a/22003440
    # for reference. It isn't obvious how to do this well, and in particular,
    # while leaving the JSON object keys out of the hash.

    # -1. Get the fields we're going to hash from the object
    fields_to_hash = field_name_ordered[endpoint]

    # 1. Dictionary to tuples
    tupes = list(d.items())
    # 2. Tuples sorted by key
    sorted_tupes = sorted(tupes, key=lambda k: k[0])
    # 2b. Get rid of fields that we're not hashing
    filtered_sorted = list(filter(lambda t: t[0] in fields_to_hash, sorted_tupes))
    # logger.info(filtered_sorted)
    # logger.info(list(map(lambda p: p[0], filtered_sorted)))

    # 3. Strip the keys
    # Why strip the keys? We don't want our field names to impact
    # the hashing value. We want to make sure the values in the object, in a consistent sort
    # order, are what get hashed. If we change field names, yes, the hash will change. But
    # our object field names are very consistent.
    # It is unclear if we're going to get consistent, cross-language hashing here.
    # It depends on how Python chooses to reprseent values as strings. If we don't quite get this right
    # the first time, it will have to be improved, and the full dataset re-disseminated.
    # p[0] is the key, p[1] is the value in the tuple list.
    # Strings must be encoded to bytes before hashing.
    just_values = list(map(lambda p: convert_to_string(p[1]), filtered_sorted))
    # 4. Append the values with no spaces.
    # logger.info(f"just_values: {just_values}")
    smooshed = "".join(just_values).strip().encode("ascii", "ignore")
    # logger.info(f"smooshed: {smooshed}")
    # This is now hashable. Run a SHA1.
    shaobj = sha1()
    shaobj.update(smooshed)
    digest = shaobj.hexdigest()
    # logger.info(f"[SHA] {digest}")

    return (digest, smooshed)


import time


def main():
    headers = {
        # THE MAGIC AUTH BEARER STRING... Use the cypress local testing values here.
        "authorization": "Bearer " + os.getenv("CYPRESS_API_GOV_JWT"),
        "x-api-key": os.getenv("CYPRESS_API_GOV_USER_ID"),
        "accept_profile": "api_v1_1_0",
    }

    if len(sys.argv) > 1:
        reports = [sys.argv[1]]
        print(f"Checking report: {reports}")
    else:
        url = f"http://localhost:3000/general?hash=neq.NOHASH&hash=not.is.null"
        res = get(url, headers=headers)
        reports = [o["report_id"] for o in res.json()]

    for report_id in reports:
        # logger.info(f"Checking {report_id}")
        for ep in ["general", "federal_awards"]:
            url = f"http://localhost:3000/{ep}?report_id=eq.{report_id}"
            # logger.info(f"Query: {url}")
            res = get(url, headers=headers)
            objs = res.json()
            # logger.info(f"Found {len(objs)} objects for {ep}:{report_id}")
            for d in objs:
                # Save the existing hash
                current_hash = d["hash"]
                (computed_hash, smooshed) = hash_dissemination_object(ep, d)
                rid = d["report_id"]
                if current_hash == computed_hash:
                    # print(f"SAME {rid}")
                    pass
                else:
                    print(
                        f"DIFFERENT {ep} {rid} dissem {current_hash} computed {computed_hash}"
                    )
                    logger.info(f"{d['report_id']}: {computed_hash} {smooshed}")
                    print(smooshed)


if __name__ in "__main__":
    main()

# b'66,47,15,11annualsingle-audit2016P.O. BOX 5752017-09-29SOUTHWEST WETLANDS INTERPRETIVE ASSOCIATIONADMINISTRATIVE OFFICERIMPERIAL BEACHDEBRA CAREYADMINISTRATIVE OFFICER953488027SWIA_DCAREY@ATT.NETSOUTHWEST WETLANDS INTERPRETIVE ASSOCIATION6195750550CAGSA_MIGRATION919332170 SOUTH EL CAMINO REAL, STE. 2132017-09-29ROLLIE MUNGERPRESIDENTOCEANSIDEROLLIE MUNGERPRESIDENTUSA473342732ROLLIE@ROLLIEMUNGERCPA.COMMUNGER & COMPANY, CPAS7607308020CA92054CENSUS2024-06-22750000non-profit2017-09-282016-12-312016-01-01unmodified_opinionNoYesNoNoNoYesNoTrue112017-09-292016-12-CENSUS-00002337332017-09-28895472UG'
# b'66,47,15,11annualsingle-audit2016P.O. BOX 5752017-09-29SOUTHWEST WETLANDS INTERPRETIVE ASSOCIATIONADMINISTRATIVE OFFICERIMPERIAL BEACHDEBRA CAREYADMINISTRATIVE OFFICER953488027SWIA_DCAREY@ATT.NETSOUTHWEST WETLANDS INTERPRETIVE ASSOCIATION6195750550CAGSA_MIGRATION919332170 SOUTH EL CAMINO REAL, STE. 2132017-09-29ROLLIE MUNGERPRESIDENTOCEANSIDEROLLIE MUNGERPRESIDENTUSA473342732ROLLIE@ROLLIEMUNGERCPA.COMMUNGER & COMPANY, CPAS7607308020CA92054CENSUS2024-06-22750000non-profit2017-09-282016-12-312016-01-01unmodified_opinionNoYesNoNoNoYesNoTrue112017-09-282016-12-CENSUS-00002337332017-09-28895472UG'
