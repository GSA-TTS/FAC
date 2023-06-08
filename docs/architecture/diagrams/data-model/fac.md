FAC Data Dissemination Data Model
```plantuml
@startuml Data Model

!define TABLE(name,desc) class name as "desc" << (T,#FFAAAA) >>
!define PRIMARY_KEY(x) <color:red>x</color>
!define FOREIGN_KEY(x) <color:blue>x</color>

hide empty attributes

TABLE(General, "General") {
  + PRIMARY_KEY(id)
  report_id
  audit_year [derived]
  fiscal_period_start
  fiscal_period_end
  period_covered
  audit_type
  organization_type
  audite_uei
  audite_ein
  audite_email
  audite_name
  audite_phone
  audite_address_line_1
  audite_city
  audite_state
  audite_zip
  auditpr_firm_name
  auditpr_ein [unique]
  auditpr_email
  auditpr_contact_name
  auditpr_contact_title
  auditpr_phone
  auditpr_address_line_1
  auditpr_city
  auditpr_state
  auditpr_zip
  cognizant_agency
  oversight_agency

}



TABLE(Award, "FederalAward") {
  + PRIMARY_KEY(id)
  + FOREIGN_KEY(General.id)
  auditee_uei
  cluster_name
  other_cluster_name
  state_cluster_name
  cluster_total
}

TABLE(Passthrough, "Passthrough") {
  + PRIMARY_KEY(id)
  + FOREIGN_KEY(General.id)
  entity_name
  uei?
}


TABLE(Finding, "Finding") {
  + PRIMARY_KEY(id)
  + FOREIGN_KEY(General.id)
  + FOREIGN_KEY(Finding.id)
  ref_number [unique]
  modified_opinion
  other_non_compliance
  material_weakness
  significant_deficiency
  other_findings
  prior_references
}
TABLE(Note, "Note") {
  + PRIMARY_KEY(id)
  + FOREIGN_KEY(General.id)
}


TABLE(FindingText, "FindingText") {
  + PRIMARY_KEY(id)
  + FOREIGN_KEY(Finding.id)
  seq_number
}

TABLE(CAPText, "CAPText") {
  + PRIMARY_KEY(id)
  + FOREIGN_KEY(Finding.id)
  seq_number
}


General "1" -- "*" Award : contains
General "1" -- "0.*" Passthrough : may-contain
General "1" -- "*" Finding : contains
Finding "1" -- "*" FindingText : contains
Finding "1" -- "*" CAPText : contains
Finding "1" -- "0,1" Finding : refers-to
General "1" -- "*" Note : contains

@enduml
```
