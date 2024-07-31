FAC Data Dissemination Data Model
```plantuml
@startuml Data Model

!define TABLE(name,desc) class name as "desc" << (T,#FFAAAA) >>
!define PRIMARY_KEY(x) <color:red>x</color>
!define FOREIGN_KEY(x) <color:blue>x</color>

hide empty attributes

TABLE(General, "General") {
    report_id
    auditee_certify_name
    auditee_certify_title
    auditor_certify_name
    auditor_certify_title
    auditor_certify_name
    auditor_certify_title
    auditee_contact_name
    auditee_email
    auditee_name
    auditee_phone
    auditee_contact_title
    auditee_address_line_1
    auditee_city
    auditee_state
    auditee_ein
    auditee_uei
    is_additional_ueis
    auditee_zip
    auditor_phone
    auditor_state
    auditor_city
    auditor_contact_title
    auditor_address_line_1
    auditor_zip
    auditor_country
    auditor_contact_name
    auditor_email
    auditor_firm_name
    auditor_foreign_address
    auditor_ein
    cognizant_agency
    oversight_agency
    date_created
    ready_for_certification_date
    auditor_certified_date
    auditee_certified_date
    submitted_date
    fac_accepted_date
    fy_end_date
    fy_start_date
    audit_year
    audit_type
    gaap_results
    sp_framework_basis
    is_sp_framework_required
    sp_framework_opinions
    is_going_concern_included
    is_internal_control_deficiency_disclosed
    is_internal_control_material_weakness_disclosed
    is_material_noncompliance_disclosed
    is_aicpa_audit_guide_included
    dollar_threshold
    is_low_risk_auditee
    agencies_with_prior_findings
    entity_type
    number_months
    audit_period_covered
    total_amount_expended
    type_audit_code
    is_public
}


TABLE(SecondaryAuditor, "SecondaryAuditor") {
  + General.report_id
  address_city
  address_state
  address_street
  address_zipcode
  auditor_ein
  auditor_name
  contact_email
  contact_name
  contact_phone
  contact_title
}


TABLE(FederalAward, "FederalAward") {
  + General.report_id
  additional_award_identification
  amount_expended
  award_reference
  cluster_name
  cluster_total
  federal_agency_prefix
  federal_award_extension 
  federal_program_name
  federal_program_total
  findings_count
  is_direct
  is_loan
  is_major
  is_passthrough_award
  loan_balance
  audit_report_type
  other_cluster_name
  passthrough_amount
  state_cluster_name
}


TABLE(Passthrough, "Passthrough") {
  + General.report_id
  award_reference
  passthrough_id
  passthrough_name
}


TABLE(Finding, "Finding") {
  + General.report_id
  award_reference
  reference_number 
  is_material_weakness
  is_modified_opinion
  is_other_findings
  is_other_matters
  is_questioned_costs
  is_repeat_finding
  is_significant_deficiency
  prior_finding_ref_numbers 
  type_requirement
}

TABLE(Note, "Note") {
  + General.report_id
  accounting_policies
  is_minimis_rate_used
  rate_explained
  content
  note_title
  contains_chart_or_table
}


TABLE(FindingText, "FindingText") {
  + General.report_id
  finding_ref_number
  contains_chart_or_table
  finding_text
}

TABLE(CAPText, "CAPText") {
  + General.report_id
  contains_chart_or_table
  finding_ref_number
  planned_action
}


TABLE(AdditionalUei, "AdditionalUei") {
  + General.report_id
  additional_uei
}


TABLE(AdditionalEin, "AdditionalEin") {
  + General.report_id
  additional_ein
}


TABLE(OneTimeAccess, "OneTimeAccess") {
  uuid
  timestamp
  api_key_id
  report_id
}


TABLE(TribalApiAccessKeyIds, "TribalApiAccessKeyIds") {
  email
  key_id
  date_added
}


TABLE(MigrationInspectionRecord, "MigrationInspectionRecord") {
  audit_year
  dbkey
  report_id
  run_datetime
  finding_text
  additional_uei
  additional_ein
  finding
  federal_award
  cap_text
  note
  passthrough
  general
  secondary_auditor
}


TABLE(InvalidAuditRecord, "InvalidAuditRecord") {
  audit_year
  dbkey
  report_id
  run_datetime
  finding_text
  additional_uei
  additional_ein
  finding
  federal_award
  cap_text
  note
  passthrough
  general
  secondary_auditor
}


TABLE(IssueDescriptionRecord, "IssueDescriptionRecord") {
  issue_detail
  issue_tag
  skipped_validation_method
}


TABLE(WaiverType, "WaiverType") {
  AUDITEE_CERTIFYING_OFFICIAL
  AUDITOR_CERTIFYING_OFFICIAL
  ACTIVE_UEI
}


General "1" -- "1,*" FederalAward : covers
General "1" -- "0,*" Passthrough : may-have
General "1" -- "0,*" SecondaryAuditor : may-have
General "1" -- "0,*" Finding : may-have
General "1" -- "0,*" FindingText : may-have
General "1" -- "0,*" CAPText : may-have
General "1" -- "0,*" AdditionalUei : may-have
General "1" -- "0,*" AdditionalEin : may-have
General "1" -- "*" Note : contains
FederalAward "1" -- "0,*" Passthrough : may-contain
Finding “1” -- “1,*” FindingText : will-have
Finding “1” -- “1,*” CAPText : will-have

@enduml
```
