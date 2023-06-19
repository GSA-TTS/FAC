FAC System Cloud boundary view
![FAC.gov  Cloud ATO boundary view]
```plantuml
@startuml Context Diagram
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(User, "User", "GranteeOrAuditor")
Person(Public, "User", "Public")
Person(Staff, "User", "FAC Staff")
Person(AgencyApp, "App", "Agency App")

note as ConnectionNote
All connections depicted are encrypted with TLS 1.2 unless otherwise noted. 
All connextions are on port 443 and use https unles otherwise noted.
All connections use TCP. 
end note


Boundary(cloudgov, "Cloud.gov Boundary") {
    Boundary(atob, "ATO Boundary") {
        Boundary(backend, "FAC application", "egress-controlled-space") {
            System(django, "FAC Web App", "Django") 
            Boundary(services, "FAC Services") {
                System(api, "REST API ", "PostgREST")
                System(scan, "Virus Scanner", "ClamAV")
            }
        }
        Boundary(proxy, "Proxy services", "egress-permitted-space"){
            System(https_proxy, "web egress proxy", "proxy for HTTP/S connections")
            System(mail_proxy, "mail egress proxy", "proxy for SMTPS connections")
        }
        Boundary(pages, "cloud.gov pages") {
            System(static, "FAC Static Site", "CG Pages") 
        }
    }
    Boundary(cloudgov-services,"Cloud.gov services") {
        System(db, "Database", "Brokered postgreSQL")
        System(s3, "PDF/XLS storage", "Brokered S3")
    }
}

    System(Login, "Login.gov", "ID provider")
    System(datagov, "api.data.gov", "Access Provider")
    System(samgov, "SAM.gov", "UEI Source")
    System(Email, "GSA Email")
    System(relic, "New Relic", "Telemetry site")
    System(dap, "DAP", "Access abalytics")
    System(clamav, "ClamAv Provider", "Vulnerability data provider")


AddRelTag("authenticated", $lineColor="#008787", $textColor="#008787")
Rel(User, django, "Submits/edits audits", $tags="authenticated") app.fac.gov
Rel(User, static, "Views static content") fac.gov
Rel(User, dap, "logs user visits data")
Rel(Public, django, "Searches for/reads information")
Rel(Staff, django, "Manages audits, roles, content", $tags="authenticated")

Rel(User, Login, "Authenticates with")
Rel(Staff, Login, "Authenticates with")
Rel(AgencyApp, datagov, "Routes requests through") api.fac.gov



Rel(datagov, api, "Searches, filters, requests audit", $tags="authenticated") port 3000
Rel(Login, django, "Autheniticated", "email address")

Rel(api, db, "Fetches (read-only) Audits") port 5432
Rel(AgencyApp, s3, "Fetches (read-only) PDF Docs")

Rel(django, https_proxy, "Uses external services (Clam DB, SAM.gov, New Relic)")
Rel(https_proxy, samgov, "Looks up UEI info")
Rel(https_proxy, clamav, "retrieves vulnerability data") port 8080
Rel(https_proxy, relic, "logs telemetry data")
Rel(django, mail_proxy, "Sends emails using")
Rel(mail_proxy, Email, "Sends emails using") port 587
Rel(django, scan, "Scans attachments")
Rel(django, db, "read/write") port 5432
Rel(django, s3, "Stores single audit packages/Excel files")
Rel(django, api, "Handles search requests") port 3000

@enduml
```