from requests import get
import os
from hashlib import sha1
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.INFO)

field_name_ordered = {
    "general": [
        "report_id",
        "audit_year",
        "total_amount_expended",
        "entity_type",
        "fy_start_date",
        "fy_end_date",
        "audit_type",
        "audit_period_covered",
        "number_months",
        "auditee_uei",
        "auditee_ein",
        "auditee_name",
        "auditee_address_line_1",
        "auditee_city",
        "auditee_state",
        "auditee_zip",
        "auditee_contact_name",
        "auditee_contact_title",
        "auditee_phone",
        "auditee_email",
        "auditee_certified_date",
        "auditee_certify_name",
        "auditee_certify_title",
        "auditor_ein",
        "auditor_firm_name",
        "auditor_address_line_1",
        "auditor_city",
        "auditor_state",
        "auditor_zip",
        "auditor_country",
        "auditor_contact_name",
        "auditor_contact_title",
        "auditor_phone",
        "auditor_email",
        "auditor_foreign_address",
        "auditor_certified_date",
        "auditor_certify_name",
        "auditor_certify_title",
        "cognizant_agency",
        "oversight_agency",
        "type_audit_code",
        "sp_framework_basis",
        "is_sp_framework_required",
        "is_going_concern_included",
        "is_internal_control_deficiency_disclosed",
        "is_internal_control_material_weakness_disclosed",
        "is_material_noncompliance_disclosed",
        "gaap_results",
        "is_aicpa_audit_guide_included",
        "sp_framework_opinions",
        "agencies_with_prior_findings",
        "dollar_threshold",
        "is_low_risk_auditee",
        "is_additional_ueis",
        "date_created",
        "fac_accepted_date",
        "ready_for_certification_date",
        "submitted_date",
        "data_source",
        "is_public",
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


def convert_to_string(o):
    if isinstance(o, datetime):
        return f"{o.date()}"
    if o is None:
        return ""
    else:
        return f"{o}"


# This is used to calculate a hash of the data for both internal and external integrity.
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
    smooshed = "".join(just_values).strip().encode("utf-8")
    # logger.info(f"smooshed: {smooshed}")
    # This is now hashable. Run a SHA1.
    shaobj = sha1()
    shaobj.update(smooshed)
    digest = shaobj.hexdigest()
    # logger.info(f"[SHA] {digest}")
    return digest


def main():
    headers = {
        # THE MAGIC AUTH BEARER STRING... Use the cypress local testing values here.
        "authorization": os.getenv("AUTH"),
        "x-api-key": "A LOCAL CYPRESS API KEY",
        "accept_profile": "api_v1_1_0",
    }
    for report_id in ["2023-06-GSAFAC-0000000688"]:
        logger.info(f"Checking {report_id}")
        for ep in ["general", "federal_awards"]:
            url = f"http://localhost:3000/{ep}?report_id=eq.{report_id}"
            logger.info(f"Query: {url}")
            res = get(url, headers=headers)
            objs = res.json()
            logger.info(f"Found {len(objs)} objects for {ep}:{report_id}")
            for d in objs:
                # Save the existing hash
                current_hash = d["hash"]
                computed_hash = hash_dissemination_object(ep, d)
                rid = d["report_id"]
                if current_hash == computed_hash:
                    print(f"SAME {rid}")
                else:
                    print(
                        f"DIFFERENT {rid} dissem {current_hash} computed {computed_hash}"
                    )


if __name__ in "__main__":
    main()

# obj
# b'00annualsingle-audit20231 Silo Circle2023-10-04Sabine CoxComptrollerStorrsSabine CoxAccounting Director060984952scox@ehmchm.orgMansfield Retirement Community, Inc.2032304809CTPATMH79QVL1406268296 State Street2023-10-04Michele Loso BoisvertPartnerNorth HavenMichele Loso BoisvertPartnerUSA060530830mloso@sewardmonde.comSeward and Monde, CPAs2032489341CT064732023-10-04750000non-profit2023-10-042023-06-302022-07-01unmodified_opinionNoNoNoNoNoYesNo142023-10-042023-06-GSAFAC-00000006882023-10-044025569UG'
# b'00annualsingle-audit20231 Silo Circle2023-10-04Sabine CoxComptrollerStorrsSabine CoxAccounting Director060984952scox@ehmchm.orgMansfield Retirement Community, Inc.2032304809CTPATMH79QVL1406268296 State Street2023-10-04Michele Loso BoisvertPartnerNorth HavenMichele Loso BoisvertPartnerUSA060530830mloso@sewardmonde.comSeward and Monde, CPAs2032489341CT064732023-10-04750000non-profit2023-10-042023-06-302022-07-01unmodified_opinionNoNoNoNoNoYesNo142023-10-042023-06-GSAFAC-00000006882023-10-044025569UG'
# api

# There are some fields that we compute in the API, or add to API objects, that are not part of the internal objects.
# Therefore, we either need to... well, we need a way to generate a hash that will/can be the same
# on both the internal and external objects. That could be by defining the fields
# we hash for each object. E.g. say "we hash fields blah, blah, and blah for general, and a, b, and c for federal awards, and ..."
# although tedious, it would be a way to guarantee the fields and order for hashing. just
# make them something we declare, for each object type.
