# Deploying

We use cloud.gov as our PaaS to provide application hosting as well as broker for Postgres and S3 instances from AWS.

We use [manifests](https://docs.cloudfoundry.org/devguide/deploy-apps/manifest.html) to configure our environments and push our applications to cloud.gov

## Contents

- [Deploying](#deploying)
  - [Contents](#contents)
  - [Tools](#tools)
  - [Cloud.gov](#cloudgov)
  - [Initial Setup](#initial-setup)
  - [Deploying Manually](#deploying-manually)
  - [Deploying Automatically](#deploying-automatically)

## Tools

* [cf-cli](https://docs.cloudfoundry.org/cf-cli/) Cloudfoundry's CLI
* [cloud.gov dashboard](https://www.cloud.gov)
* [cloud.gov deploy action](https://github.com/18F/cg-deploy-action)

## Cloud.gov

- Organization: `gsa-10x-prototyping`
- Spaces: `dev`

- Apps: fac-dev
    - Manifest: [manifest-dev.yml](../backend/manifests/manifest-dev.yml)
    - route: [fac-dev.app.cloud.gov](https://fac-dev.app.cloud.gov)

## Initial Setup

This process is used to provision services in an otherwise empty Organization + Space within cloud.gov.

```shell
# Authenticate
cf login -a api.fr.cloud.gov  --sso

# Target desired org and space
cf target -o {ORG NAME} -s {SPACE NAME}

# Provision an Postgres AWS RDS database service
cf create-service aws-rds small-psql fac_dev_db

# Provision an S3 bucket
cf create-service s3 basic-sandbox fac_dev_s3
```

## Deploying Manually

After you've authenticated and targeted the desired org/space, push the application with

```shell
# Push the development app using `dev manifest
cf push -f manifests/manifest-dev.yml
```

## Deploying Automatically

When a new commit is pushed to `main`, Github Actions automatically deploys the latest code to [fac-dev](https://fac-dev.app.cloud.gov/).

The workflow to deploy the latest code can be found in [deploy.yml](.github/workflows/deploy.yml) and uses the [cloud.gov deploy action](https://github.com/18F/cg-deploy-action).
