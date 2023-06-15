FAC Data Dissemination Data Model
```plantuml
@startuml Data Model

!define TABLE(name,desc) class name as "desc" << (T,#FFAAAA) >>
!define PRIMARY_KEY(x) <color:red>x</color>
!define FOREIGN_KEY(x) <color:blue>x</color>

hide empty attributes

TABLE(General, "General") {
  + report_id
  audit_year [derived]
  period_covered
  audit_type
  organization_type
  audite_uei
  audite_ein
  cognizant_agency
  oversight_agency
  transition_dates
  general [JSON]
}



TABLE(Award, "FederalAward") {
  + FOREIGN_KEY(General.report_id)
  + seq_number
  cluster_name
  other_cluster_name
  state_cluster_name
  cluster_total
  award [JSON]
}

TABLE(Passthrough, "Passthrough") {
  + FOREIGN_KEY(General.report_id)
  + uei
  passthrough [JSON]
}


TABLE(Finding, "Finding") {
  + FOREIGN_KEY(General.report_id)
  + ref_number
  finding [JSON]
}

TABLE(Note, "Note") {
  + FOREIGN_KEY(General.id)
  + seq_number
  note [JSON]
}


TABLE(FindingText, "FindingText") {
  + FOREIGN_KEY(General.report_id)
  + ref_number
  + seq_number
  finding_text [JSON]
}

TABLE(CAPText, "CAPText") {
  + FOREIGN_KEY(General.report_id)
  + FOREIGN_KEY(Finding.ref_number)
  + seq_number
  cap_text [JSON]
}


General "1" -- "*" Award : covers
General "1" -- "0.*" Passthrough : may-contain
Award "1" -- "*" Finding : contains
Finding "1" -- "*" FindingText : contains
Finding "1" -- "*" CAPText : contains
Award "1" -- "*" Note : contains

@enduml
```
