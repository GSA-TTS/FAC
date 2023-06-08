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
  audit_year
  + FOREIGN_KEY(Auditee.id)
  + FOREIGN_KEY(Auditor.id)

}

TABLE(Auditee, "Auditee") {
  + PRIMARY_KEY(id)
  uei [unique]
  ein [unique]
  email
  contact_name
  contact_title
  phone
  address_line_1
  city
  state
  zip
}

TABLE(Auditor, "Auditor") {
  + PRIMARY_KEY(id)
  firm_name
  ein [unique]
  email
  contact_name
  contact_title
  phone
  address_line_1
  city
  state
  zip



}

TABLE(Award, "FederalAward") {
  + PRIMARY_KEY(id)
  + FOREIGN_KEY(General.id)
  _program_info_
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
Auditee "1" -- "*" General : submits
Auditor "1" -- "*" General : audits

@enduml
