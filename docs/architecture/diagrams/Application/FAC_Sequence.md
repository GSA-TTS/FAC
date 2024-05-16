# FAC System User Interaction view

## Looks like updates are needed

![FAC.gov  User Interaction view]

```plantuml
@startuml User Interaction Diagram
Actor GranteeOrAuditor
Actor Public
Actor AgencyApp
Actor Staff

Participant “FAC.gov” as FAC
Participant “postgREST.FAC.gov” as FacREST
Participant “Login.gov” as LoginGov
Participant “appData.gov” as DataGov

Database “DataStore” as DB
Database "S3" as S3

autonumber 
== Submission ==
GranteeOrAuditor -> FAC : Grantee Accesses FAC
FAC -> LoginGov : Redirects for authentication
LoginGov -> FAC : Redirects to FAC
GranteeOrAuditor -> FAC : Fetches Submission
DB -> FAC : Fetches previously saved structured data
S3 -> FAC : Fetches previously saved xlsx docs
FAC -> GranteeOrAuditor : Makes previous submission available for editing
GranteeOrAuditor -> FAC : Makes Submission
FAC -> DB : Persists structured data
FAC -> S3 : Persists xlxs docs


autonumber
== Public Access ==
Public -> FAC : Unauthenticated public searches for audit reports
FAC -> DB : Retrieves searched audits
FAC -> S3 : Retrieves pdfs associated with audits
FAC -> Public : Makes info available for viewing and downloading

autonumber
== Agency Access ==
AgencyApp -> DataGov :  Rewquests data via REST from FAC
DataGov -> FACREST : Forwards token-authorized API to FAC
FACREST <-> DB : Retrieves searched audits
FACREST -> DataGov : Makes info available
DataGov -> AgencyApp : Returns API results
AgencyApp <-> FAC : Retrieves pdfs associated with audits
FAC <-> S3 : Retrieves pdfs associated with audits


autonumber
== Staff Access (Future) ==
Staff -> FAC : Grantee Accesses FAC
FAC -> LoginGov : Redirects for authentication
LoginGov -> FAC : Redirects to FAC
Staff -> FAC : Fetches Content or Submissions
DB -> FAC : Provides previously saved structured data
S3 -> FAC : Provides previously saved xlsx docs
FAC -> Staff : Makes previous submission available for viewing
Staff -> FAC : Makes Content changes
FAC -> DB : Persists content data

@enduml
```