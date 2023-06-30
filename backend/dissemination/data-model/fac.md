FAC Data Dissemination Data Model
```plantuml
@startuml Data Model

!define TABLE(name,desc) class name as "desc" << (T,#FFAAAA) >>
!define PRIMARY_KEY(x) <color:red>x</color>
!define FOREIGN_KEY(x) <color:blue>x</color>

hide empty attributes

TABLE(General, "General") {
    + report_id
    audit_period_covered
    audit_type
    audit_year                        /'22 AUDITYEAR '/
    auditee_address_line_1
    hist_auditee_address_line_2            /' STREET2 Historic data '/
    auditee_certified                 /' 22 AUDITEEDATESIGNED. AUDITEEDATESIGNED is derived by certification status timestamp'/
    auditee_certify_name  
    auditee_certify_title
    auditee_city
    auditee_contact_name
    auditee_contact_title             /'22 AUDITEENAMETITLE and AUDITEETITLE'/
    auditee_email
    hist_auditee_fax                       /' Historic data '/
    auditee_name
    auditee_phone
    auditee_state
    auditee_uei
    auditee_zip
    auditor_address_line_1 
    hist_auditor_address_line_2            /' CPASTREET2 Historic data '/
    auditor_certified                 /' 22 CPADATESIGNED. CPADATESIGNED is derived by certification status timestamp'/
    auditor_city
    auditor_contact_name
    auditor_contact_title             /' 22 CPANAMETITLE '/
    auditor_country
    auditor_ein
    auditor_email
    hist_auditor_fax                       /' Historic data '/
    auditor_firm_name 
    auditor_foreign_addr              /' 22 CPAFOREIGN'/
    auditor_phone
    auditor_state
    auditor_title
    auditor_zip
    cognizant_agency
    cognizant_agency_over             /' 22 COG_OVER '/
    hist_completed_date                    /' Historic data '/
    component_date_received           /' Historic data '/
    condition_or_deficiency_major_program 
    hist_copies                            /' Historic data '/
    current_or_former_findings        /'22 CYFINDINGS '/
    data_source                       /'GFAC or CFAC '/
    hist_date_firewall                     /' Historic data '/
    date_published
    date_received
    hist_date_received_other               /' Historic data '/ 
    dollar_threshold
    hist_duns                              /' Historic data '/
    dup_reports
    ein
    ein_subcode
    entity_type
    fac_accepted_date
    finding_ref_num
    form_date_received 
    fy_end_date 
    fy_start_date
    going_concern
    hist_image                             /' Historic data '/
    initial_date_received 
    is_public
    low_risk 
    material_noncompliance 
    material_weakness 
    material_weakness_major_program
    multiple_auditors                 /'22 MULTIPLE_CPAS '/
    hist_multiple_duns                     /' Historic data '/
    multiple_eins_covered
    multiple_ueis_covered
    number_months
    oversight_agency
    pdf_url                           /' GFAC '/
    hist_previous_completed_on_date    /' Historic data '/  
    hist_previous_date_firewall            /' Historic data '/
    hist_previous_date_published           /' Historic data '/
    prior_year_schedule 
    questioned_costs 
    report_required  
    hist_reportable_condition              /' Historic data '/
    hist_reportable_condition_major_program    /' Historic data '/
    sd_material_weakness, 
    sd_material_weakness_major_program
    significant_deficiency
    hist_significant_deficiency_major_program  /' Historic data.  22 SIGNIFICANTDEFICIENCY_MP '/
    special_framework
    special_framework_required 
    suppression_code  
    total_fed_expenditures 
    type_audit_code
    hist_type_of_entity                    /' Historic data '/
    type_report_financial_statements 
    type_report_major_program  
    type_report_special_purpose_framework
      

  "AGENCYCFDA" ?

}

TABLE(Auditor, "GenAuditor") {
  + General.report_id
  + auditor_seq_number
    auditor_city
    auditor_contact
    auditor_country 
    auditor_ein 
    auditor_email
    auditor_fax 
    auditor_firm_name 
    auditor_foreign_addr
    auditor_phone
    auditor_state 
    auditor_street1 
    auditor_title 
    auditor_zip_code
 
    "VERSION" ? /' Discuss with Matt '/
}


TABLE(Award, "FederalAward") {
  + General.report_id
  + award_seq_number 
  additional_award_identification 
  amount_expended 
  arra 
  audit_report_type 
  cfdaprogramname
  cluster_name
  cluster_total
  elecauditsid
  federal_agency_prefix 
  federal_program_total 
  hist_findings                                    /' Historic data '/
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
  hist_questioned_costs2                             /' Historic data '/ 
  research_and_development 
  state_cluster_name
  subrecipient_amount 
  three_digit_extension 
  type_report_major_program
  type_requirement


  "CFDA2" VARCHAR2(2 BYTE) COLLATE "USING_NLS_COMP", ?	
}

TABLE(Passthrough, "Passthrough") {
  + Award.award_seq_number /' Old ELECSAUDIT '/
  + Award.report_id
  + passthrough_id
  passthrough_name
}


TABLE(Finding, "Finding") {
  + Award.award_seq_number /' To be added to GFAC '/
  + Award.report_id
  + finding_ref_number /' GFAC '/
  material_weakness
  modified_opinion
  other_findings
  other_non_compliance
  prior_finding_ref_numbers
  questioned_costs
  repeat_finding
  significant_deficiency
  type_requirement

  findingrefnums ?
}

TABLE(Note, "Note") {
  + General.report_id
  + note_seq_number
  content
  note_index
  note_title
  type_id 
  version /' Is this the latest version? Discuss with Matt.  Is this required in General? '/
}


TABLE(FindingText, "FindingText") {
  + Finding.report_id
  + Finding.finding_ref_number
  charts_tables
  finding_text
}

TABLE(CAPText, "CAPText") {
  + Finding.report_id
  + Finding.finding_ref_number
  cap_text
  charts_tables
}


TABLE(Revision, "Revision") {
  /' Maybe needed only for Historical data' 
  Is this needed for GFAC? - Decision to be made.'/
}

General "1" -- "*" Award : covers
General "1" -- "0,*" Auditor : may-have
General "1" -- "0,*" Revision : may-have
Award "1" -- "0,*" Passthrough : may-contain
Award "1" -- "*" Finding : contains
General "1" -- "*" Note : contains
FindingText “1” -- “*” Finding : applies-to
CAPText “1” -- “*” Finding : applies-to

@enduml
```
