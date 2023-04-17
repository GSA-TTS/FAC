```mermaid
    C4Context
      title FAC System Architecture

      Person(User, "User", "Auditee/Auditor")
      Person(Public, "User", "Public")
      Person(Staff, "User", "FAC Staff")
      Person(Agency, "User", "Agency User")
      Person(AgencyApp, "App", "Agency App")


      Boundary(cloudgov, "Cloud.gov Boundary") {
          Boundary(atob, "ATO Boundary") {
              Boundary(backend, "FAC application", "egress-controlled-space") {
                  Boundary(django, "FAC Web App", "port 8080") {
                      System(admin, "Django Admin interface")
                      System(submissions, "Django authenticated frontend")
                      System(publicinfo, "Django unauthenticated frontend")
                      System(pvtinfo, "Django authenticated frontend")
                  }
                  Boundary(services, "FAC Services") {
                      System(api, "REST API", "PostgREST")
                      System(scan, "Virus Scanner", "ClamAV")
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
      System(Email, "GSA Email")

      %% The following line is not understood by Mermaid;
      %% Try uncommenting it in the online Mermaid editor (https://mermaid.live/edit)
      %% AddRelTag("authenticated", $lineColor="#008787", $textColor="#008787")
      Rel(User, django, "Submits/edits audits")
      Rel(Public, django, "Searches for/reads information")
      Rel(Agency, django, "Searches for/reads non-public information")
      Rel(Staff, django, "Manages audits, roles, content")

      Rel(User, Login, "Authenticates with")
      Rel(Staff, Login, "Authenticates with")
      Rel(Agency, Login, "Authenticates with")
      Rel(AgencyApp, datagov, "Routes requests through")

      Rel(datagov, api, "Searches, filters, requests audit", "via api.data.gov", $tags="authenticated")
      Rel(Login, backend, "Provides identities", "email address")

      Rel(api, db, "Fetches (read-only) Audits")
      Rel(api, s3, "Fetches (read-only) Audit Attachments")

      Rel(django, https_proxy, "Looks up UEI info")
      Rel(https_proxy, samgov, "Looks up UEI info")
      Rel(django, mail_proxy, "Sends emails using")
      Rel(mail_proxy, Email, "Sends emails using")
      Rel(django, scan, "Scans attachments")
      Rel(django, db, "read/write")
      Rel(backend, s3, "Stores single audit packages/Excel files")

```
