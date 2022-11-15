# Terraform

This directory holds the terraform modules for maintaining your complete persistent infrastructure.

Prerequisite: install the `jq` JSON processor (`brew install jq`) and terraform
(`brew install terraform` or
<https://learn.hashicorp.com/tutorials/terraform/install-cli>)

## Initial setup

1. Manually run the bootstrap module following instructions under `Terraform State Credentials`
1. Setup CI/CD Pipeline to run Terraform
  1. Copy bootstrap credentials to your CI/CD secrets using the instructions in the base README
  1. Create a cloud.gov SpaceDeployer by following the instructions under `SpaceDeployers`
  1. Copy SpaceDeployer credentials to your CI/CD secrets using the instructions in the base README
1. Manually Running Terraform
  1. Follow instructions under `Set up a new environment` to create your infrastructure

## Terraform State Credentials

The bootstrap module is used to create an s3 bucket for later terraform runs to store their state in.

### Bootstrapping the state storage s3 bucket for the first time

1. Run `terraform init` in this directory.
1. Run `./run.sh plan` to verify that the proposed changes are what you expect
1. Run `./run.sh apply` to set up the bucket and retrieve those credentials
1. Follow instructions under `Use bootstrap credentials` to save the access credentials and bucket names.
1. Ensure that `./import.sh` includes a line and correct IDs for any resources created. The IDs to use in `import.sh` are given in the Terraform output as `[id=....]`.
1. Run `./teardown_creds.sh` to remove the space deployer account used to create the s3 bucket

### To make changes to the bootstrap module

*This should not be necessary in most cases.*

1. Run `terraform init`
1. If you don't have terraform state locally:
    1. run `./import.sh`
    1. optionally run `./run.sh apply` to include the existing outputs in the state file
1. Make your changes
1. Continue from step 2 of the boostrapping instructions

### Retrieving existing bucket credentials

1. Run `./run.sh show`
1. Follow instructions under `Use bootstrap credentials`

#### Use bootstrap credentials

1. Add the following to `~/.aws/credentials`
    ```
    [fac-terraform-backend]
    aws_access_key_id = <access_key_id from bucket_credentials>
    aws_secret_access_key = <secret_access_key from bucket_credentials>
    ```

1. Copy `bucket` from `bucket_credentials` output to the backend block of `staging/providers.tf` and `production/providers.tf`

## SpaceDeployers

A [SpaceDeployer](https://cloud.gov/docs/services/cloud-gov-service-account/) account is required to run terraform or
deploy the application from the CI/CD pipeline. Create a new account by running:

`../bin/ops/create_service_account.sh -s <SPACE_NAME> -u <ACCOUNT_NAME>`

## Set up a new environment manually

The below steps rely on you first configuring access to the Terraform state in s3 as described in [Terraform State Credentials](#terraform-state-credentials).

1. `cd` to the environment you are working in

1. Set up a SpaceDeployer
    ```bash
    # create a space deployer service instance that can log in with just a username and password
    # the value of < SPACE_NAME > should be `staging` or `production` depending on where you are working
    # the value for < ACCOUNT_NAME > can be anything, although we recommend
    # something that communicates the purpose of the deployer
    # for example: circleci-deployer for the credentials CircleCI uses to
    # deploy the application or <your_name>-terraform for credentials to run terraform manually
    ../../bin/ops/create_service_account.sh -s <SPACE_NAME> -u <ACCOUNT_NAME> > secrets.auto.tfvars
    ```

    The script will output the `username` (as `cf_user`) and `password` (as `cf_password`) for your `<ACCOUNT_NAME>`. Read more in the [cloud.gov service account documentation](https://cloud.gov/docs/services/cloud-gov-service-account/).

    The easiest way to use this script is to redirect the output directly to the `secrets.auto.tfvars` file it needs to be used in

1. Run terraform from your new environment directory with
    ```bash
    terraform init
    terraform plan
    ```

1. Apply changes with `terraform apply`.

1. Remove the space deployer service instance if it doesn't need to be used again, such as when manually running terraform once.
    ```bash
    # <SPACE_NAME> and <ACCOUNT_NAME> have the same values as used above.
    ../../bin/ops/destroy_service_account.sh -s <SPACE_NAME> -u <ACCOUNT_NAME>
    ```

## Structure

Each environment has its own module, which relies on a shared module for everything except the providers code and environment specific variables and settings.

```
- bootstrap/
  |- main.tf
  |- providers.tf
  |- variables.tf
  |- run.sh
  |- teardown_creds.sh
  |- import.sh
- <env>/
  |- main.tf
  |- providers.tf
  |- secrets.auto.tfvars
  |- variables.tf
- shared/
  |- s3/
     |- main.tf
     |- providers.tf
     |- variables.tf
  |- database/
     |- main.tf
     |- providers.tf
     |- variables.tf
  |- domain/
     |- main.tf
     |- providers.tf
     |- variables.tf
```

In the shared modules:
- `providers.tf` contains set up instructions for Terraform about Cloud Foundry and AWS
- `main.tf` sets up the data and resources the application relies on
- `variables.tf` lists the required variables and applicable default values

In the environment-specific modules:
- `providers.tf` lists the required providers
- `main.tf` calls the shared Terraform code, but this is also a place where you can add any other services, resources, etc, which you would like to set up for that environment
- `variables.tf` lists the variables that will be needed, either to pass through to the child module or for use in this module
- `secrets.auto.tfvars` is a file which contains the information about the service-key and other secrets that should not be shared

In the bootstrap module:
- `providers.tf` lists the required providers
- `main.tf` sets up s3 bucket to be shared across all environments. It lives in `production` to communicate that it should not be deleted
- `variables.tf` lists the variables that will be needed. Most values are hard-coded in this module
- `run.sh` Helper script to set up a space deployer and run terraform. The terraform action (`show`/`plan`/`apply`/`destroy`) is passed as an argument
- `teardown_creds.sh` Helper script to remove the space deployer setup as part of `run.sh`
- `import.sh` Helper script to create a new local state file in case terraform changes are needed