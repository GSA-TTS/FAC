FAC Data Dissemination Data Model
```plantuml
@startuml Data Model

!define TABLE(name,desc) class name as "desc" << (T,#FFAAAA) >>
!define PRIMARY_KEY(x) <color:red>x</color>
!define FOREIGN_KEY(x) <color:blue>x</color>

hide empty attributes

TABLE(General, "General") {
  + report_id
    auditee_certify_name
    auditee_certify_title 
    auditee_contact
    auditee_email 
    auditee_fax 
    auditee_name
    auditee_name_title?
    auditee_phone
    auditee_title 
    auditee_street1 
    auditee_street2 
    auditee_city 
    auditee_state 
    ein
    multiple_ein
    duns
    multiple_duns
    uei
    multiple_uei
    ein_subcode 
    auditee_zip_code
    auditor_phone
    auditor_fax 
    auditor_state 
    auditor_city
    auditor_title 
    auditor_street1 
    auditor_street2
    auditor_zip_code
    auditor_country 
    auditor_contact
    auditor_email
    auditor_firm_name 
    auditor_foreign_addr
    auditor_ein 
    multiple_auditors
    sequence_number ?
    is_public
    pdf_urls
    cognizant_agency
    oversight_agency
    cognizant_agency_over 
    fac_accepted_date 
    initial_date_received
    fy_end_date 
    fy_start_date 
    previous_completed_on 
    previous_date_published
    completed_date 
    component_date_received 
    audit_type
    reportable_condition
    significant_deficiency
    condition_or_deficiency_major_program 
    current_or_former_findings 
    dollar_threshold 
    dup_reports 
    entity_type 
    going_concern 
    low_risk 
    material_noncompliance 
    material_weakness 
    material_weakness_major_program
    number_months
    period_covered 
    prior_year_schedule 
    questioned_costs 
    report_required 
    special_framework
    special_framework_required 
    total_fed_expenditures 
    type_of_entity 
    type_report_financial_statements 
    type_report_major_program
    type_report_special_purpose_framework 
    is_public 
    data_source 
    auditee_date_signed
    auditor_date_signed
    type_report_financial_statements
    reportable_condition
    material_weakness
    material_noncompliance
    going_concern
    type_report_major_program
    dollar_threshold
    low_risk
    report_required
    total_fed_expenditures
    condition_or_deficiency_major_program
    material_weakness_major_program
    questioned_costs
    current_or_former_findings
    prior_year_schedule
    dup_reports
    form_date_received
    date_published
    previous_date_published
    agency_cdfa ?
    special_framework
    special_framework_required
    type_report_special_purpose_framework
	"COPIES" VARCHAR2(2 BYTE) COLLATE "USING_NLS_COMP", 
	"FINDINGREFNUM" CHAR(1 BYTE) COLLATE "USING_NLS_COMP", 
	"IMAGE" NUMBER(1,0), 
	"INITIALDATE" DATE, 
	"DATERECEIVEDOTHER" DATE, 
	"SD_MATERIALWEAKNESS" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP", 
	"SD_MATERIALWEAKNESS_MP" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP", 
	"SIGNIFICANTDEFICIENCY" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP", 
	"SIGNIFICANTDEFICIENCY_MP" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP", 
	"SUPPRESSION_CODE" VARCHAR2(4 BYTE) COLLATE "USING_NLS_COMP", 
	"TYPEAUDIT_CODE" VARCHAR2(4 BYTE) COLLATE "USING_NLS_COMP", 
	"OPEID" VARCHAR2(4000 BYTE) COLLATE "USING_NLS_COMP", 
	"DATETOED" DATE, 
	"DATEFINISHED" DATE, 
	"TYPEFINDING" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP", 
	"TYPEFUNDING" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP"

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
	"VERSION" NUMBER(2,0), 
}


TABLE(Award, "FederalAward") {
  + General.report_id
  + award_seq_number
  cfda_prefix
  cfda_ext
  award_identification
  fed_prog_name
  major_program
  amount
  cluster_name
  other_cluster_name
  state_cluster_name
  cluster_total
  program_total
  loan_balance
  type_requirement
  questioned_costs
  research_and_development
  direct
  type_report_major_program
  arra
  loans
  state_cluster_name
  other_cluster_name
  passthrough_award
  passthrough_amount
	"FINDINGS" VARCHAR2(3 BYTE) COLLATE "USING_NLS_COMP", 
	"FINDINGREFNUMS" VARCHAR2(100 BYTE) COLLATE "USING_NLS_COMP", 
	"CFDA2" VARCHAR2(2 BYTE) COLLATE "USING_NLS_COMP", 
	"TYPEREPORT_MP_OVERRIDE" VARCHAR2(1 BYTE) COLLATE "USING_NLS_COMP", 
	"FINDINGSCOUNT" NUMBER(7,0), 
	"CFDAPROGRAMNAME" VARCHAR2(300 BYTE) COLLATE "USING_NLS_COMP", 

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
