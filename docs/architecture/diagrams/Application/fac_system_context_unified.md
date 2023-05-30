FAC System Cloud boundary view
![FAC.gov  Cloud ATO boundary view]
```plantuml
@startuml Context Diagram
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(User, "User", "GranteeOrAuditor")
Person(Public, "User", "Public")
Person(Staff, "User", "FAC Staff")
Person(AgencyApp, "App", "Agency App")

note as EncryptionNote
All connections depicted are encrypted with TLS 1.2. 
end note
note as PortsNote
All connextions are on port 443 and use https except the following
which use different ports as noted in the diagram:
FAC Web App, PostgREST, ClamAV and PostgreSQL.
end note


Boundary(cloudgov, "Cloud.gov Boundary") {
    Boundary(atob, "ATO Boundary") {
        Boundary(backend, "FAC application", "egress-controlled-space") {
            System(django, "FAC Web App", "port 8080") 
            Boundary(services, "FAC Services") {
                System(api, "REST API", "PostgREST, port 3000")
                System(scan, "Virus Scanner", "ClamAV, port 8080")
            }
        }
        Boundary(proxy, "Proxy services", "egress-permitted-space"){
            System(https_proxy, "web egress proxy", "proxy for HTTP/S connections")
            System(mail_proxy, "mail egress proxy", "proxy for SMTPS connections")
        }
    }
    Boundary(cloudgov-services,"Cloud.gov services") {
        System(db, "Database", "postgres, port 5432")
        System(s3, "PDF/XLS storage", "Brokered S3")
    }
}

    System(Login, "Login.gov", "ID provider")
    System(datagov, "api.data.gov", "Access Provider")
    System(samgov, "SAM.gov", "UEI Source")
    System(Email, "GSA Email, port 587")
    System(relic, "New Relic", "Telemetry site")
    System(dap, "DAP", "Access abalytics")
    System(clamav, "ClamAv Provider", "Vulnerability data provider")


AddRelTag("authenticated", $lineColor="#008787", $textColor="#008787")
Rel(User, django, "Submits/edits audits", $tags="authenticated")
Rel(User, dap, "logs user visits data")
Rel(Public, django, "Searches for/reads information")
Rel(Staff, django, "Manages audits, roles, content", $tags="authenticated")

Rel(User, Login, "Authenticates with")
Rel(Staff, Login, "Authenticates with")
Rel(AgencyApp, datagov, "Routes requests through")



Rel(datagov, api, "Searches, filters, requests audit", "via api.data.gov", $tags="authenticated")
Rel(Login, django, "Autheniticated", "email address")

Rel(api, db, "Fetches (read-only) Audits")
Rel(AgencyApp, s3, "Fetches (read-only) PDF Docs")

Rel(django, https_proxy, "Uses external services (Clam DB, SAM.gov, New Relic)")
Rel(https_proxy, samgov, "Looks up UEI info")
Rel(https_proxy, clamav, "retrievesvulnerability data")
Rel(https_proxy, relic, "logs telemetry data")
Rel(django, mail_proxy, "Sends emails using")
Rel(mail_proxy, Email, "Sends emails using")
Rel(django, scan, "Scans attachments")
Rel(django, db, "read/write")
Rel(django, s3, "Stores single audit packages/Excel files")
Rel(django, api, "Handles search requests")

@enduml
```