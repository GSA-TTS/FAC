# Terraform
This directory holds the terraform modules for maintaining your complete persistent infrastructure.

## Pre-Requisites
If you don't already have it, download [Docker Desktop](https://www.docker.com/products/docker-desktop/)

You must be running version 8+ of the CF client for the helper scripts to work and WSL2 Ubuntu/Linux for terraform.

### WSL2 Installation
Open command line or powershell as admin.
```
wsl --list --online
wsl --install -d Ubuntu
```
**IMPORTANT**: Next, enable WSL2 integration with Docker Desktop.
- Settings > Resources > WSL2 Integration > Ubuntu (enable)

Once this happens, ensure that you fully reboot your computer. Once restarted, open Docker Desktop, and open your IDE of choice (VSCode for example.) When you select a new terminal window, you will see Ubuntu(WSL). Open that terminal and run
```
sudo apt update
sudo apt full-upgrade -y
```

If it fails to upgrade packages, run the following commands (Ref: [Stack Overflow Page](https://stackoverflow.com/a/63578387))
```
netsh winsock reset
netsh int ip reset all
netsh winhttp reset proxy
ipconfig /flushdns
```
And restart your computer once more.

## Core Dependencies

Next install cf-cli v8 on WSL2 Ubuntu or Linux:
```bash
# ...first add the Cloud Foundry Foundation public key and package repository to your system
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
# ...then, update your local package index, then finally install the cf CLI
sudo apt-get update
sudo apt-get install cf8-cli
```

Next install AWS CLI on WSL2 Ubuntu or Linux:
[AWS CLI Install Instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
```bash
# WSL2
sudo snap install aws-cli --classic

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# aws doesnt work with an x509 error? This fixed it on my WSL2 Ubuntu
pip install --upgrade cryptography==36.0.2
```

Next install terraform on WSL2 Ubuntu or Linux:
```bash
sudo snap install terraform --classic
```

Finally, install necessary requirements:
```
sudo apt install jq
sudo apt install npm
sudo apt install zip
```

## Terraform State Credentials

A deployer account will be provided for each environment. Access to specific environments depends on successful merge and deploy of your onboarding ticket.

You can view the specific services with `cf services` and associated key for the deployer service with `cf service-keys <service-name> <service-key-name>`. To obtain the deployer credentials for a specific environment, run the following commands:
```bash
# This implies that you are in the environment specific folder
cd terraform/<environment>
../../bin/ops/get_service_account.sh -o gsa-tts-oros-fac -s <environment> -u <service-key-name> >> secrets.auto.tfvars
```
This will update a `secrets.auto.tfvars` in the directory for use with terraform.

> [!NOTE]
> You can use `bin/ops/create_service_account.sh` to create a new one if something happens to the existing one.

## Bootstrapping the state storage s3 bucket for the first time
By default, we use a [partial s3 configuration](https://developer.hashicorp.com/terraform/language/backend) for all environments. This will be handled automatically when you run `terraform init`, and requires use of of a `backend.tfvars` file to store sensitive credentials to access the s3 bucket.

> [!WARNING]
> *This should not be necessary in most cases.* Running the below command will initialize your directory to work directly with the LIVE terraform state that exists in the s3 bucket. As a best practice, it is imperative that if you are running terraform from your local machine, you create and utilize backups of the terraform.tfstate for your specific environment. You, by running this command, are taking authority of the terraform state underneath all of our other operations, and as such, assume full responsibility for infrastructure changes that are run after this point.
```bash
terraform init \
  --backend-config=../shared/config/backend.tfvars \
  --backend-config=key=terraform.tfstate."$(basename "$(pwd)")"
```

## Modifying common files
> [!WARNING]
> The meta module is responsible for all environments configuration and common files. Any file with `-managed.tf` is a file managed by this module, and should not be changed manually. All changes should be done by changing the template, creating a backup of the `terraform.tfstate.meta`, running `terraform init`, `terraform plan`, and `terraform apply` to generate the local files, create a `pull request`, and merge into `main` before any other `pull requests` can merge, as doing so will cause issues with the terraform state, since the merge that does not have the new files will overwrite the updated `terraform.tfstate.meta`.

```bash
# ./FAC/terraform/meta/
├── meta
│   ├── bootstrap-env
│   │   ├── templates
│   │   │   ├── init.sh-template
│   │   │   ├── main.tf-template
│   │   │   ├── providers.tf-template
│   │   │   └── variables.tf-template
```

## Structure

Each environment has its own module, which relies on a shared module for everything except the providers code and environment specific variables and settings.

```bash
# ./FAC/terraform/
├── dev
│   ├── dev.tf
│   ├── dev.tf-example
│   ├── imports.tf
│   ├── init.sh
│   ├── providers-managed.tf
│   ├── variables-managed.tf
│   └── variables.tf
├── meta
│   ├── bootstrap
│   │   ├── import.sh
│   │   ├── main.tf
│   │   ├── providers.tf
│   │   ├── run.sh
│   │   ├── teardown_creds.sh
│   │   └── variables.tf
│   ├── bootstrap-env
│   │   ├── deployer.tf
│   │   ├── environment.tf
│   │   ├── providers.tf
│   │   ├── space.tf
│   │   ├── templates
│   │   │   ├── init.sh-template
│   │   │   ├── main.tf-template
│   │   │   ├── providers.tf-template
│   │   │   └── variables.tf-template
│   │   └── variables.tf
│   ├── config.tf
│   ├── imports.tf
│   ├── init.sh
│   ├── meta.tf
│   ├── providers.tf
│   ├── README.md
│   ├── update-managed-files.py
│   └── variables.tf
├── metabase-config
│   └── config
│       ├── backend.tfvars
│       └── preview.tfvars
├── preview
│   ├── imports.tf
│   ├── init.sh
│   ├── preview.tf
│   ├── preview.tf-example
│   ├── providers-managed.tf
│   ├── variables-managed.tf
│   └── variables.tf
├── production
│   ├── imports.tf
│   ├── init.sh
│   ├── production.tf
│   ├── production.tf-example
│   ├── providers-managed.tf
│   ├── variables-managed.tf
│   └── variables.tf
├── README.md
├── shared
│   ├── config
│   │   ├── backend.tfvars
│   │   ├── dev.tfvars
│   │   ├── preview.tfvars
│   │   ├── production.tfvars
│   │   └── staging.tfvars
│   └── modules
│       ├── app
│       │   ├── app.tf
│       │   ├── outputs.tf
│       │   ├── prepare_app.sh
│       │   ├── providers.tf
│       │   ├── readme.md
│       │   └── variables.tf
│       ├── archived_modules
│       │   ├── https-proxy
│       │   │   ├── acl.tftpl
│       │   │   ├── https-proxy.tf
│       │   │   ├── outputs.tf
│       │   │   ├── prepare-proxy.sh
│       │   │   ├── providers.tf
│       │   │   ├── proxy.zip
│       │   │   ├── README.md
│       │   │   ├── test
│       │   │   │   ├── https-proxy-test.tf
│       │   │   │   ├── index.html
│       │   │   │   ├── prepare-client.sh
│       │   │   │   ├── README.md
│       │   │   │   ├── terraform.tfvars-template
│       │   │   │   └── validate.sh
│       │   │   └── variables.tf
│       │   └── sandbox-proxy
│       │       ├── acl.tftpl
│       │       ├── https-proxy.tf
│       │       ├── outputs.tf
│       │       ├── prepare-proxy.sh
│       │       ├── providers.tf
│       │       ├── proxy.zip
│       │       ├── README.md
│       │       ├── test
│       │       │   ├── https-proxy-test.tf
│       │       │   ├── index.html
│       │       │   ├── prepare-client.sh
│       │       │   ├── README.md
│       │       │   ├── terraform.tfvars-template
│       │       │   └── validate.sh
│       │       └── variables.tf
│       ├── cg-logshipper
│       │   ├── cg-logshipper.tf
│       │   ├── fluentbit_config
│       │   │   └── fluentbit.conf
│       │   ├── logshipper.zip
│       │   ├── outputs.tf
│       │   ├── prepare-logshipper.sh
│       │   ├── providers.tf
│       │   ├── readme.md
│       │   └── variables.tf
│       ├── cors
│       │   ├── cors-script.sh
│       │   ├── cors.tf
│       │   ├── dev-cors.json
│       │   ├── preview-cors.json
│       │   ├── production-cors.json
│       │   ├── staging-cors.json
│       │   └── variables.tf
│       ├── env
│       │   ├── clamav.tf
│       │   ├── cors.tf
│       │   ├── env.tf
│       │   ├── https-proxy.tf
│       │   ├── logshipper.tf
│       │   ├── metabase.tf
│       │   ├── newrelic.tf
│       │   ├── policies.tf
│       │   ├── postgrest.tf
│       │   ├── providers.tf
│       │   ├── scanner.tf
│       │   ├── smtp-proxy.tf
│       │   └── variables.tf
│       ├── metabase
│       │   ├── metabase.tf
│       │   ├── outputs.tf
│       │   ├── providers.tf
│       │   ├── readme.md
│       │   └── variables.tf
│       ├── newrelic
│       │   ├── alerts.tf
│       │   ├── dashboards.tf
│       │   ├── high_level_page.json.tftpl
│       │   ├── logreview.tf
│       │   ├── management_widgets.json.tftpl
│       │   ├── monitoring_dashboard.json.tftpl
│       │   ├── monitoring.tf
│       │   ├── providers.tf
│       │   ├── readme.md
│       │   ├── variables.tf
│       │   └── widgets.json.tftpl
│       ├── scanner
│       │   ├── outputs.tf
│       │   ├── prepare-scanner.sh
│       │   ├── providers.tf
│       │   ├── readme.md
│       │   ├── scanner.tf
│       │   ├── scanner.zip
│       │   └── variables.tf
│       └── stream-proxy
│           ├── app
│           │   └── nginx.conf
│           ├── outputs.tf
│           ├── prepare-proxy.sh
│           ├── providers.tf
│           ├── proxy.zip
│           ├── README.md
│           ├── stream-proxy.tf
│           ├── testconfig.sh
│           ├── tests
│           │   └── default
│           │       ├── app
│           │       │   └── index.html
│           │       ├── prepare-client.sh
│           │       ├── README.md
│           │       ├── stream-proxy-test.tf
│           │       ├── terraform.tfvars-template
│           │       └── validate.sh
│           └── variables.tf
└── staging
    ├── imports.tf
    ├── init.sh
    ├── providers-managed.tf
    ├── staging.tf
    ├── staging.tf-example
    ├── variables-managed.tf
    └── variables.tf
```

In the shared `terraform/shared/modules/env` module:
- `env.tf` sets up the common resources for all environments
- `variables.tf` lists the per-env-configurable variables, and the production defaults

In the environment-specific modules:
- `providers.tf` lists the required providers
- `main.tf` calls the shared Terraform `env` module, but this is also a place where you can add any other services, resources, etc, which you would like to set up for that environment
- `variables.tf` lists the variables that will be needed, either to pass through to the child module or for use in this module
- `deployer-creds.auto.tfvars` is a file which contains the information about the service-key and other secrets that should not be shared

In the bootstrap module:
- `providers.tf` lists the required providers
- `main.tf` sets up s3 bucket to be shared across all environments. It lives in `production` to communicate that it should not be deleted
- `variables.tf` lists the variables that will be needed. Most values are hard-coded in this module
- `run.sh` Helper script to set up a space deployer and run terraform. The terraform action (`show`/`plan`/`apply`/`destroy`) is passed as an argument
- `teardown_creds.sh` Helper script to remove the space deployer setup as part of `run.sh`
- `import.sh` Helper script to create a new local state file in case terraform changes are needed 
