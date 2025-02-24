## CI/CD Operations

**Introduction:**
We use a plethora of CI/CD mechanisms in the FAC, largely surrounding terraform and github workflows. Inside those mechanisms, there are various items that serve to handle our process which revolve around testing, scanning, and deploying. This document is considered a living document and should be updated as new mechanisms or items are introduced.

**Development Overview:**
Largely, the scope of operations can be viewed in the below graph, which illustrate how a new piece of code, feature or implementation may be introduced to the ecosystem. A developer will take on a task, work on that task locally, create a pull request, that pull request will be tested, it is approved, and then merged into dev, automatically merged into staging the following day, and then released to production once a week, with ad-hoc releases also acceptable.

```mermaid
flowchart LR
    subgraph "Planning, Research & Development"
    A@{ shape: circle, label: "Task/Feature/
    Enhancement" } -->|Create Branch| B(Development)
    B --> C{Development Complete}
    end
    C --> D[Docker]
    subgraph "Local (Features)"
    D --> E(Django Testing)
    D --> F(Cypress Testing)
    D --> G(Smoke Testing/
    Feature Testing)
    end

    C --> H[Sandbox]
    J(Deployment Test)

    C --> L[Preview]
    E <--> F
    F <--> G

    subgraph "Cloud (Features)"
    H & L --> J(Deployment Test)
    end
    E & F & G & J --> K[PR Ready]

    M@{ shape: circle, label: "PR Opened" }
    M --> N@{ shape: div-rect, label: "Linting
    Django Testing
    Cypress Testing
    a11y Testing
    Terraform Plan
    Code Coverage" }
    N --> |Approve| O{Merge to Dev}
```

**Pull Request Overview:**
By and large, when a pull request has been opened, one of the two above paths has been tested to qualify it as Pull Request ready. We follow a similar path to manual local testing when a PR opens, however, the underlying system is slightly different depending on what has been done. If a PR does not change core dependencies, then it will run necessary tests using the current [GHCR containter](https://github.com/GSA-TTS/FAC/pkgs/container/fac%2Fweb-container), and after merging, it will rebuild and overwrite it. If a PR does change dependencies, the GHCR version is ignored, and all tests run on a builder.

```mermaid
flowchart LR
    A{Pull Request Opened}
    A --> B@{ shape: processes, label: "Linting" }
    B --> C@{ shape: subproc, label: "flake8
    Black
    Bandit
    mypy
    djlint
    npm run check-all
    terraform fmt" }
    A --> D@{ shape: processes, label: "Terraform" }
    D --> E@{ shape: subproc, label: "Terraform Plan"}
    A --> X
    X@{ shape: circle, label: "Check For
    Dependency Change" }
    X-- No Dependency Change --> F@{ shape: processes, label: "Test" }
    X-- Dependency Change --> H@{ shape: processes, label: "Test" }
    subgraph GHCR
    F --> G@{ shape: subproc, label: "Django
    a11y
    cypress"}
    end
    subgraph Builder
    H --> I@{ shape: subproc, label: "Django
    a11y
    cypress"}
    end
    C & E & G & I --> K@{ shape: dbl-circ, label: "Review" }
```

**Deployments:**
When a PR is approved and ready to merge, a bunch of processes are triggered to again, validate all operational components related to a deployment. Some of these operations are redundant, but they ensure that the new code base does not cause any conflict in any way. We operate under the assumption that if it passes in the pull request, we have high stability, however we run them again as a means to attempt to catch any outliers.


```mermaid
flowchart LR
    A{Merge to main}
    A --> B@{ shape: processes, label: "Linting" }
    A --> C@{ shape: processes, label: "Build Container" }
    subgraph Test
    C --> D@{ shape: subprocess, label: "Publish to GHCR" }
    E[Fetch GHCR Image] --> F@{ shape: processes, label: "Run Test Suite" }
    end
    subgraph Terraform
    G[Terraform Apply]
    G-- deploy --> H(Dev Modules)
    G-- deploy --> I(Meta Modules)
    end
    F --> G
    subgraph Deploy
    direction TB
    J@{ shape: subprocess, label: "Install Dependencies" }
    K@{ shape: subprocess, label: "Compile Assets" }
    L@{ shape: subprocess, label: "Update Service Keys" }
    M@{ shape: subprocess, label: "Deploy to Cloud.gov" }
    N@{ shape: subprocess, label: "DB Table Check" }
    J --> K --> L --> M --> N
    end
    O@{ shape: subprocess, label: "Record to New Relic" }
    Terraform --> O
    O --> Deploy
    Deploy --> P@{shape: dbl-circ, label: "ZAP Scan"}
    subgraph Trivy
    S{{Merge Event}} --> T@{shape: subprocess, label: "Vulnerability Scan Containers"}
    end
    A --> S
```

While all environments generally deploy the same way, it is heavily front-loaded in the dev environment. Staging differs slightly
```mermaid
flowchart LR
    A{Merge to staging}
    A --> B@{ shape: processes, label: "Linting" }
    A --> E
    subgraph Test
    E[Fetch GHCR Image] --> F@{ shape: processes, label: "Run Test Suite" }
    end
    subgraph Terraform
    G[Terraform Apply]
    G-- deploy --> H(Staging Modules)
    end
    F --> G
    subgraph Deploy
    direction TB
    J@{ shape: subprocess, label: "Install Dependencies" }
    K@{ shape: subprocess, label: "Compile Assets" }
    L@{ shape: subprocess, label: "Update Service Keys" }
    M@{ shape: subprocess, label: "Deploy to Cloud.gov" }
    N@{ shape: subprocess, label: "DB Table Check" }
    J --> K --> L --> M --> N
    end
    O@{ shape: subprocess, label: "Record to New Relic" }
    Terraform --> O
    O --> Deploy
    Deploy --> P@{shape: circ, label: "ZAP Scan"}
    Deploy --> Q@{shape: dbl-circ, label: "Regression Tests"}
    subgraph Trivy
    S{{Merge Event}} --> T@{shape: subprocess, label: "Vulnerability Scan Containers"}
    end
    A --> S
```
And production differs in the the removal of regression tests, with a supplemental deployment step
```mermaid
flowchart LR
    A{Release}
    A --> B@{ shape: processes, label: "Linting" }
    A --> E
    subgraph Test
    E[Fetch GHCR Image] --> F@{ shape: processes, label: "Run Test Suite" }
    end
    subgraph Terraform
    G[Terraform Apply]
    G-- deploy --> H(Production Modules)
    end
    F --> G
    subgraph Deploy
    direction TB
    J@{ shape: subprocess, label: "Install Dependencies" }
    K@{ shape: subprocess, label: "Compile Assets" }
    L@{ shape: subprocess, label: "Update Service Keys" }
    Q@{ shape: subprocess, label: "Backup Database" }
    M@{ shape: subprocess, label: "Deploy to Cloud.gov" }
    N@{ shape: subprocess, label: "DB Table Check" }
    J --> K --> L --> Q --> M --> N
    end
    O@{ shape: subprocess, label: "Record to New Relic" }
    Terraform --> O
    O --> Deploy
    Deploy --> P@{shape: circ, label: "ZAP Scan"}
    subgraph Trivy
    S{{Merge Event}} --> T@{shape: subprocess, label: "Vulnerability Scan Containers"}
    end
    A --> S
```

**Automated Tasks:**
Automated tasks are run on a schedule daily, with the exception of the backup operations in each environment, which run every 2 hours during operational times (EST Start) -> (PST End of Day).
```mermaid
flowchart TB
    X{{Daily Operations}} ---> C & E & F & G & A & N
    subgraph Scheduler
    C@{ shape: processes, label: "Run Materialized Views" }
    E@{ shape: processes, label: "Regression Tests" }
    F@{ shape: subprocess, label: "Update Trivy Cache" }
    subgraph Containers
    G@{ shape: processes, label: "Rebuild Containers" }
    G --> Q(Postgrest)
    G --> R(ClamAV)
    G --> S(Web Container)
    end
    subgraph Check Tables
    A@{ shape: subprocess, label: "Check DB Tables" }
    A --> H(Dev) & I(Staging) & J(Prod)
    end
    subgraph Backups
    direction TB
    B@{ shape: processes, label: "Run Backups" }
    B -- Every 2 Hours --> K(Dev) & L(Staging) & M(Prod)
    end
    subgraph Staging Deployment
    N@{ shape: subprocess, label: "Check for Diffs" }
    D@{ shape: processes, label: "Deploy to Staging" }
    N -- Diff --> D
    N -- No Diff--> P@{ shape: dbl-circ, label: "End" }
    end
    end
```
