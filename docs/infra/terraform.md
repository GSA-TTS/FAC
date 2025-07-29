## Terraform

### Introduction
We use a variety of modules, custom or shared in order to handle our underlying infrastructure components. They are broken apart into environments, with a `shared` folder that handles the components that are not unique and will be applied to each environment.

### Using terraform at the FAC
The majority of documentation can be found in the [Folder Readme](../../terraform/README.md) which details specific installation instructions. Some steps may be dependent on OS(Mac, WSL2, Linux) particularly for installing the terraform binary and setting it in your $PATH.

Each custom module has their own readme which includes a small overview, diagram (if applicable) and usage parameters.

### Terraform Map
Detailed below is a reference to, with a description of, each of our various modules.

**Environments:**
* [Dev](../../terraform/dev/dev.tf)
* [Staging](../../terraform/staging/staging.tf)
* [Production](../../terraform/production/production.tf)
* [Preview](../../terraform/preview/preview.tf)
* [Sandbox](../../terraform/sandbox/sandbox.tf)
* [Meta](../../terraform/meta/meta.tf)
    * Each of these module files details their respective parameters that are passed when using the `cloudfoundry/cloudfoundry` provider. Each module has a `source = "../shared/modules/env"` with the exception of sandbox which has a source of `source = "../shared/modules/sandbox"`. The two folders are relatively the same, and hold the components that go into the environments. The `env/` folder exclusively references components for Dev, Staging, Production & Preview, where the `sandbox/` folder exclusively references the components for Sandbox. Meta is an exception here, but more information is available below.

**Meta and the Environment Bootstrap:**
* [Meta - Config](../../terraform/meta/config.tf)
    * The config file is responsible for handling permissions for developers within the system. When a team member is onboarded/offboarded, this file should be updated to reflect the accurate list of active developers who need access to the systems. Information on roles and scopes can be found on the [docs](https://docs.cloudfoundry.org/concepts/roles.html)
* [Bootstrap - Deployer](../../terraform/meta/bootstrap-env/deployer.tf)
    * The deployer file is responsible for handling service accounts and their permissions, and having a space deployer account is necessary for both local terraform work and github deployment operations.
* [Bootstrap - Environment](../../terraform/meta/bootstrap-env/environment.tf)
    * This file is largely depreciated under the old bootstrap module, and doesn't need to be modified. It is primarily used as a means to work with terraform locally.
* [Bootstrap - Module Files](../../terraform/meta/bootstrap-env/modulefiles.tf)
    * When we deploy Meta, it catalogs and overrides local files on disk. These files are suffixed with a `-managed` tag on the file. Modification to this file is not expressely necessary unless we have a file that needs to be managed in each environment. Modifications to any `-managed` file should be done in the [templates](../../terraform/meta/bootstrap-env/templates/) folder.
* [Bootstrap - Space](../../terraform/meta/bootstrap-env/space.tf)
    * Spaces is responsible for managing global space permissions within the organization for the `meta/config.tf` file.

**Core Modules:**
* [Logshipper](../../terraform/shared/modules/cg-logshipper/readme.md)
    * A lightweight application responsible for firehosing another applications logs and storing them in an s3 bucket, along with sending them to New Relic for telemetry purposes.
* [New Relic](../../terraform/shared/modules/newrelic/readme.md)
    * A compilation of various terraform based new relic functions.
* [Fac File Scanner](../../terraform/shared/modules/scanner/readme.md)
    * A lightweight flask application that periodically scans a targeted folder in the live s3 bucket for viruses and malware, post submission. This is done as an ATO requirement to retroactively perform scans. We also perform scans when the file gets submitted through the UI of the application.
* [Application](../../terraform/shared/modules/app/readme.md)
    * A module responsible for deploying the core application to the Sandbox environment.
* [Metabase](../../terraform/shared/modules/metabase/readme.md)
    * A module for deploying the metabase service to any environment. This is used for dashboarding purposes.

**Shared Components:**
* [ClamAV](../../terraform/shared/modules/env/clamav.tf)
    * Configuration file for ClamAV Rest Application.
* [CORS](../../terraform/shared/modules/env/cors.tf)
    * Configuration file for setting CORS.
* [Base Environment](../../terraform/shared/modules/env/env.tf)
    * Configuration file for layering components in an environment that all of them will need. (S3, RDS)
* [Proxy](../../terraform/shared/modules/env/https-proxy.tf)
    * Configuration file for Caddy Forward Proxy which details the explicit allowlist for the public internet.
* [Logshipper](../../terraform/shared/modules/env/logshipper.tf)
    * Configuration file for the Logshipper Application
* [New Relic](../../terraform/shared/modules/env/newrelic.tf)
    * Calling file for the New Relic components.
* [Network Policies](../../terraform/shared/modules/env/policies.tf)
    * A singular file which outlines all network policies between applications, used instead of having the policies defined in their respective application module code.
* [Postgrest](../../terraform/shared/modules/env/postgrest.tf)
    * Configuration file for the PostgREST API.
* [FAC File Scanner](../../terraform/shared/modules/env/scanner.tf)
    * Configuration file for the File Scanner module.
* [SMTP Proxy](../../terraform/shared/modules/env/smtp-proxy.tf)
    * Largely OBE'd. A configuration file for the SMTP Proxy.

**Sandbox Components that aren't shared across all environments:**
* [Application](../../terraform/shared/modules/sandbox/app.tf)
    * Configuration file for deploying the FAC Application.
* [Metabase](../../terraform/shared/modules/sandbox/metabase.tf)
    * Configuration file for deploying the Metabase Application.

