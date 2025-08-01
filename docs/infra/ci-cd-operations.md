## CI/CD Operations

### Introduction
We use a variety of CI/CD mechanisms in the FAC surrounding terraform and github workflows. Inside those mechanisms, there are various items that serve to handle our process of testing, scanning, and deploying. This document is considered a living document and should be updated as new mechanisms or items are introduced.

### Development
The scope of operations can be viewed in the below graph, which illustrate how a new piece of code, feature or implementation may be introduced to the ecosystem. A developer will take on a task, work on that task locally, create a pull request, that pull request will be tested, it is approved, and then merged into dev, automatically merged into staging the following day, and then released to production once a week, with ad-hoc releases also acceptable.

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

### Pull Requests
By and large, when a pull request has been opened, one of the two above paths has been tested to qualify it as Pull Request ready. We follow a similar path to manual local testing when a PR opens, however, the underlying system is slightly different depending on what has been done. If a PR does not change core dependencies, then it will run necessary tests using the current [GHCR container](https://github.com/GSA-TTS/FAC/pkgs/container/fac%2Fweb-container), and after merging, it will rebuild and overwrite it. If a PR does change dependencies, the GHCR version is ignored, and all tests run on a builder.

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

### Deployments
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

While all environments generally deploy the same way, it is front-loaded with rebuilding the container before deploying to the dev environment. Staging differs slightly:
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
And production differs in the the removal of regression tests, with a supplemental deployment step:
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

Finally, a high level illustration of what the process looks like to take a feature to production:
```mermaid
flowchart LR
    A@{ shape: processes, label: "Local Development" }
    C@{ shape: processes, label: "Pull Request" }

    A --- B
    B --o C@{ shape: processes, label: "Pull Request" }

    subgraph Local
    B@{ shape: processes, label: "Testing" }
    end

    subgraph Cloud
    D@{ shape: processes, label: "Deploy Sandbox" }
    E@{ shape: processes, label: "Deploy Preview" }
    end
    A --> D & E
    Cloud --> C

    subgraph Review
    C --> F{Approval}
    C --> G{Enhancements}
    end
    G -...-> A

    subgraph Dev
    I@{ shape: processes, label: "Merge 'branch' to 'main'" }
    H@{ shape: processes, label: "Deploy 'main' to development environment" }
    end
    F --> I --> H
    J{{Scheduler}}
    Dev === J
    J === K
    subgraph Staging
    K@{ shape: processes, label: "Merge 'main' to 'prod'" }
    L@{ shape: processes, label: "Deploy 'prod' to staging environment" }
    end
    K --> L
    subgraph Prod
    M@{ shape: processes, label: "Deploy 'prod' to production environment" }
    end
    N{{Weekly Release}} --> M
    Staging --> N
```

### Automated Tasks
Automated tasks are run on a schedule, with each schedule having different times or frequencies.
||Staging Deploy|Materialized Views|Regression Tests|Trivy Cache Update|Check Tables|Rebuild Containers|Backups|
|:---|----|---|---|---|---|---|---|
|**Time**|10am UTC Mon-Sa|6am UTC|9am UTC Mon-Fri|12am UTC|12am/12pm UTC|5am UTC Sun|12p, 2p, 4p, 6p, 8p, 10p UTC|
|**Cron**|'0 10 * * 1-6'| '0 6 * * *'|'0 9 * * 1-5'|'0 0 * * *'|'0 */12 * * *'|'0 5 * * 0'|'0 12,14,16,18,20,22/2 * * *'|
```mermaid
flowchart TB
    X{{Daily Operations}} ---> C & E & F & A & N
    Y{{Weekly Operations}} ---> G
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
    B --> K(Dev) & L(Staging) & M(Prod)
    end
    subgraph Staging Deployment
    N@{ shape: subprocess, label: "Check for Diffs" }
    D@{ shape: processes, label: "Deploy to Staging" }
    N -- Diff --> D
    N -- No Diff--> P@{ shape: dbl-circ, label: "End" }
    end
    end
```

### CI/CD Map
Detailed below is a reference to, with a description of, each of our various components.

**Ops:**
* [Auto Merge Staging PR](../.github/workflows/daily-merge-staging-pr.yml)
    * This works in parallel with [Create PR to Staging](../.github/workflows/pull_request-to-staging.yml) as a means to automate staging merges. This approves the PR with a PAT.
* [Build Docker Container](../.github/workflows/containers-build-fac-container.yml)
    * This workflow does a `docker build` on our system, much like if you were performing this locally, gives the container a tag, and then pushes it to GHCR.
* [Create PR to Staging](../.github/workflows/pull_request-to-staging.yml)
    * This checks to see if there has been a commit in 24 hours, and if so, creates a pull request, tags it, and then approves it with the Github secret access token [GITHUB_TOKEN](https://docs.github.com/en/enterprise-server@3.16/actions/security-for-github-actions/security-guides/automatic-token-authentication#about-the-github_token-secret).
* [Pull & Push Containers to GCHR](../.github/workflows/containers-push-upstream-to-ghcr.yml)
    * Pulls the latest ClamAV & Postgrest container from their respective sources, scans them with [Aquasecurity's Trivy](https://github.com/aquasecurity/trivy), and then publishes to our GHCR.
* [Terraform Plan](../.github/workflows/terraform-plan-env.yml)
    * Used to create a terraform plan on pull requests to illustrate what operations will be performed when merging to a specific environment, impacting changes on the infrastructure.
* [Terraform Apply](../.github/workflows/terraform-apply-env.yml)
    * Used to run a terraform app on merge events to execute the operations generated in a pull requests plan to a specific environment, impacting changes on the infrastructure.
* [Trivy](../.github/workflows/scanning-trivy.yml)
    * Runs [Aquasecurity's Trivy](https://github.com/aquasecurity/trivy) against our containers.
* [Trivy Cache Updater](../.github/workflows/scanning-rebuild-trivy-cache.yml)
    * Rebuilds the vulnerability database for Trivy and stores in the Github Cache
* [ZAP](../.github/workflows/scanning-zap-scan.yml)
    * Crawls a live environment with [ZAP](https://www.zaproxy.org/) using our [configuration](../zap.conf).

**Testing:**
* [Cypress Test (Container)](../.github/workflows/testing-cypress-container.yml)
    * This sets up everything necessary for cypress to run in a headless environment, on a github runner that enables it to run as a pull request check.
* [Cypress](../.github/workflows/testing-cypress-regression-tests.yml)
    * This file handles all non-container run tests using Cypress against a live environment.
* [Daily Regressions Tests](../.github/workflows/testing-daily-regression.yml)
    * A lightweight cron and caller file that invokes a regression test run on `staging` daily.
* [Lint](../.github/workflows/pull_request-linting.yml)
    * Used to perform linting across the board for main application code and fail if necessary, preventing a merge/deploy if there are errors.
* [Lint (Terraform)](../.github/workflows/terraform-lint.yml)
    * Used to perform linting on terraform specific files.
* [Pull Request Checks](../.github/workflows/pull_request-checks.yml)
    * All logic used to perform tests and ensure that a pending pull request can be eligable to merge into a branch.
* [Testing From Build](../.github/workflows/testing-from-build.yml)
    * Runs the test suite on a built docker container. Used when there are changes to core dependencies (`requirements.txt`, `dev-requirements.txt`, `Dockerfile`, `package.json` and `static files`).
* [Testing From GHCR](../.github/workflows/testing-from-ghcr.yml)
    * Runs the test suite against the previous versions published container in GHCR if there are no changes to core dependencies.

**Deployments:**
* [Deploy Application](../.github/workflows/deploy-application.yml)
    * This workflow is the basis for deploying an application to any environement, starting by setting up all necessary dependencies and then deploying to cloud.gov. It is called by multiple files, based on the environment that is set to deploy.
* [Deploy Development](../.github/workflows/deploy-development.yml), [Deploy Preview](../.github/workflows/deploy-preview.yml), [Deploy Staging](../.github/workflows/deploy-staging.yml) and [Deploy Production](../.github/workflows/deploy-production.yml)
    * The main caller files that describe the steps necessary for a workflow run to deploy a specific environment. Only small changes differ between these files.
* [Record Deployment on New Relic](../.github/workflows/deploy-record-newrelic-deployment.yml)
    * Creates a "marker" on the New Relic activity chart, accessible via the New Relic application, to signify that a deployment has occured.
* [Staging Scheduled Deployment](../.github/workflows/daily-deploy-staging.yml)
    * Necessary steps to ensure code from main(dev) is eligable to move to the prod(staging) environment.

**Data:**
* [Backup Scheduler](../.github/workflows/fac_backup-scheduler.yml) and [Run Backups on Schedule](../.github/workflows/fac_backup-util-scheduled.yml)
    * These work in parallel to invoke the [FAC Backup Utility](https://github.com/GSA-TTS/fac-backup-utility) via a [bash script](../backend/fac_backup-util.sh) to perform an RDS table backup and S3 content backup every 2 hours during EST Start of Day and PST End of Day.
    * [FAC Backup Util](../.github/workflows/fac-backup-util.yml) invokes the [FAC Backup Utility](https://github.com/GSA-TTS/fac-backup-utility) via a [bash script](../backend/fac-backup-util.sh) on demand.
* [Check Tables Scheduler](../.github/workflows/fac_backup-check-tables-scheduler.yml) and [Check Tables](../.github/workflows/fac_backup-check-tables.yml)
    * These work in parallel to invoke the [FAC Backup Utility](https://github.com/GSA-TTS/fac-backup-utility) via a [bash script](../backend/fac-backup-util.sh) to perform a table check on the RDS using a manifest to determine if there are any discrepancies in our tables (missing, lost, untracked).

* [Export Audit Data to CSV](../.github/workflows/weekly-export-audit-data-to-csv.yml)
    * Invokes a django command to [export data](../backend/support/management/commands/export_data_audit.py) to CSV format.
* [Materialized Views](../.github/workflows/daily-materialized-views.yml)
    * Calls the Django function [materialized views](../backend/dissemination/management/commands/materialized_views.py) to run the [create materialized views](../backend/dissemination/sql/create_materialized_views.sql) sql.
