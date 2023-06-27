FAC Data Dissemination Data Model
```plantuml
@startuml Data Model

!define TABLE(name,desc) class name as "desc" << (T,#FFAAAA) >>
!define PRIMARY_KEY(x) <color:red>x</color>
!define FOREIGN_KEY(x) <color:blue>x</color>

hide empty attributes

TABLE(General, "General") {
    audit_period_covered
    audit_type
    auditee_address_line_1
    auditee_address_line_2 
    auditee_certified 
    auditee_certify_name  
    auditee_certify_title
    auditee_city
    auditee_contact_name
    auditee_contact_title 
    auditee_email
    auditee_fax 
    auditee_fiscal_period_end 
    auditee_fiscal_period_end 
    auditee_name
    auditee_phone
    auditee_state
    auditee_uei
    auditee_zip
    auditor_address_line_1 
    auditor_address_line_2 
    auditor_certified 
    auditor_city
    auditor_contact_name
    auditor_contact_title 
    auditor_country
    auditor_ein
    auditor_email
    auditor_fax 
    auditor_firm_name 
    auditor_foreign_addr   
    auditor_phone
    auditor_state
    auditor_title
    auditor_zip
    cognizant_agency
    cognizant_agency_over 
    completed_date  
    component_date_received  
    condition_or_deficiency_major_program 
    current_or_former_findings 
    data_source 
    date_firewall 
    date_published 
    dollar_threshold
    duns 
    dup_reports
    ein
    ein_subcode
    entity_type
    fac_accepted_date
    form_date_received 
    fy_end_date 
    fy_start_date
    going_concern
    image 
    initial_date_received 
    is_public
    low_risk 
    material_noncompliance 
    material_weakness 
    material_weakness_major_program
    multiple_auditors 
    multiple_duns 
    multiple_eins_covered
    multiple_ueis_covered
    number_months
    oversight_agency
    pdf_url     
    previous_completed_on  
    previous_date_firewall 
    previous_date_published 
    prior_year_schedule 
    questioned_costs 
    report_required  
    reportable_condition 
    reportable_condition_major_program 
    sd_material_weakness, 
    sd_material_weakness_major_program
    significant_deficiency
    significant_deficiency_major_program 
    special_framework
    special_framework_required 
    suppression_code  
    total_fed_expenditures 
    type_audit_code
    type_of_entity 
    type_report_financial_statements 
    type_report_major_program  
    type_report_special_purpose_framework
  + report_id      

  "COPIES" VARCHAR2(2 BYTE) COLLATE "USING_NLS_COMP", ?
	"INITIALDATE" DATE, ?
  "DATERECEIVEDOTHER" DATE,  ?
	"OPEID" VARCHAR2(4000 BYTE) COLLATE "USING_NLS_COMP", ?
	"DATETOED" DATE, ?
	"DATEFINISHED" DATE, ? 
	"TYPEFINDING" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP", ?
  "DATERECEIVED" ?
  "FINDINGREFNUM" ?
  "AGENCYCFDA" ?
  "AUDITEECERTIFYNAME" ?
  "TYPEFUNDING" ?
}

TABLE(Auditor, "GenAuditor") {
    + General.report_id
  + auditor_seq_number
    auditor_phone
    auditor_fax 
    auditor_state 
    auditor_city
    auditor_title 
    auditor_street1 
    auditor_zip_code
    auditor_country 
    auditor_contact
    auditor_email
    auditor_firm_name 
    auditor_foreign_addr
    auditor_ein 
	"VERSION" NUMBER(2,0), ?
}


TABLE(Award, "FederalAward") {
  + award_seq_number 
  + General.report_id
  additional_award_identification 
  amount_expended 
  arra 
  audit_report_type 
  cluster_name
  cluster_total
  elecauditsid
  federal_agency_prefix 
  federal_program_total 
  findingscount
  is_direct 
  is_guaranteed 
  is_major 
  is_passed 
  loan_balance_at_audit_period_end 
  loans
  number_of_audit_findings 
  other_cluster_name
  passthrough_amount
  passthrough_award
  program_name 
  research_and_development 
  state_cluster_name
  subrecipient_amount 
  three_digit_extension 
  type_report_major_program
  type_requirement

  questioned_costs ?
  findings ?
  cfdaprogramname ?
  "CFDA2" VARCHAR2(2 BYTE) COLLATE "USING_NLS_COMP", ?
	"TYPEREPORT_MP_OVERRIDE" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP",?
}

TABLE(Passthrough, "Passthrough") {
  + Award.report_id
  + Award.award_seq_number
  + passthrough_seq_number
  passthrough [JSON]
}


TABLE(Finding, "Finding") {
  + Award.report_id
  + Award.award_seq_number
  + finding_seq_number
  finding_ref_number
  modified_opinion
  other_non_compliance
  material_weakness
  significant_deficiency
  other_findings
  questioned_costs
  repeat_finding
  prior_finding_ref_number
  type_requirement
}

TABLE(Note, "Note") {
  + Award.report_id
  + Award.award_seq_number
  + note_seq_number
  type_id [choice??]
  version
  content
  title
  "REPORTID": ["Note", "report_id"]
  "NOTE_INDEX": ["Note", "note_index"]

}


TABLE(FindingText, "FindingText") {
  + Finding.report_id
  + Finding.award_seq_number
  + Finding.finding_seq_number
  + finding_text_seq_number
  charts_tables
  finding_text
}

TABLE(CAPText, "CAPText") {
  + Finding.report_id
  + Finding.award_seq_number
  + Finding.finding_seq_number
  + cap_text_seq_number
  charts_tables
  cap+text
  finding_ref_number [derivabke??]
}


TABLE(Revision, "Revision") {
}

General "1" -- "*" Award : covers
General "1" -- "0,*" Auditor : may-have
General "1" -- "0,*" Revision : may-have
Award "1" -- "0.*" Passthrough : may-contain
Award "1" -- "*" Finding : contains
Finding "1" -- "*" FindingText : contains
Finding "1" -- "*" CAPText : contains
Award "1" -- "*" Note : contains

@enduml
```
