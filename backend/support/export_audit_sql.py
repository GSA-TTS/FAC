select_additional_eins = (
    "select * from {api_version}.additional_eins where audit_year = '{audit_year}'"
)

select_additional_ueis = (
    "select * from {api_version}.additional_ueis where audit_year = '{audit_year}'"
)

select_general_information = (
    "select * from {api_version}.general where audit_year = '{audit_year}'"
)


select_corrective_action_plans = "select * from {api_version}.corrective_action_plans where audit_year = '{audit_year}'"


select_federal_awards = (
    "select * from {api_version}.federal_awards where audit_year = '{audit_year}'"
)


select_findings = (
    "select * from {api_version}.findings where audit_year = '{audit_year}'"
)


select_findings_text = (
    "select * from {api_version}.findings_text where audit_year = '{audit_year}'"
)


select_notes_to_sefa = (
    "select * from {api_version}.notes_to_sefa where audit_year = '{audit_year}'"
)


select_passthrough = (
    "select * from {api_version}.passthrough where audit_year = '{audit_year}'"
)


select_secondary_auditors = (
    "select * from {api_version}.secondary_auditors where audit_year = '{audit_year}'"
)


select_all_additional_eins = "select * from {api_version}.additional_eins"

select_all_additional_ueis = "select * from {api_version}.additional_ueis"

select_all_general_information = "select * from {api_version}.general"


select_all_corrective_action_plans = (
    "select * from {api_version}.corrective_action_plans"
)


select_all_federal_awards = "select * from {api_version}.federal_awards"


select_all_findings = "select * from {api_version}.findings"


select_all_findings_text = "select * from {api_version}.findings_text"


select_all_notes_to_sefa = "select * from {api_version}.notes_to_sefa"


select_all_passthrough = "select * from {api_version}.passthrough"


select_all_secondary_auditors = "select * from {api_version}.secondary_auditors"


select_fed_year_additional_eins = (
    "select * from {api_version}.additional_eins "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)

select_fed_year_additional_ueis = (
    "select * from {api_version}.additional_ueis "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)

select_fed_year_general_information = (
    "select * from {api_version}.general where "
    "fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}'"
)


select_fed_year_corrective_action_plans = (
    "select * from {api_version}.corrective_action_plans "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)


select_fed_year_federal_awards = (
    "select * from {api_version}.federal_awards "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)


select_fed_year_findings = (
    "select * from {api_version}.findings "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)


select_fed_year_findings_text = (
    "select * from {api_version}.findings_text "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)


select_fed_year_notes_to_sefa = (
    "select * from {api_version}.notes_to_sefa "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)


select_fed_year_passthrough = (
    "select * from {api_version}.passthrough "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)


select_fed_year_secondary_auditors = (
    "select * from {api_version}.secondary_auditors "
    "where report_id in "
    "(select report_id from {api_version}.general "
    "where fac_accepted_date>='{fac_accepted_date_start}' "
    "and fac_accepted_date<= '{fac_accepted_date_end}')"
)
