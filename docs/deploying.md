# Deploying

We use [cloud.gov](https://cloud.gov/) as our PaaS to provide application hosting as well as broker for Postgres and S3 instances from AWS.

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

- [cf-cli](https://docs.cloudfoundry.org/cf-cli/) Cloudfoundry's CLI
  - Mac install of v8 needed for Cloud.gov: `brew install cloudfoundry/tap/cf-cli@8`
- [cloud.gov dashboard](https://www.cloud.gov)
- [cloud.gov deploy action](https://github.com/18F/cg-deploy-action)
- [application logs](https://logs.fr.cloud.gov/) with search and dashboard

## Cloud.gov

- Organization: `gsa-tts-oros-fac`
- Spaces: `dev`, `staging`, `production`

- Apps: gsa-fac
    - Manifests: [/backend/manifests](../backend/manifests)
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

# Create a User-Provided Service Instance to store credentials
cf create-user-provided-service fac-key-service -p '{"SAM_API_KEY":"{your Sam.Gov API key}"}'
```

## Deploying Manually

After you've authenticated and targeted the desired org/space, push the application with

```shell
# Push the development app using `dev manifest
cf push -f manifests/manifest-dev.yml
```

## Deploying Automatically

The simple answer is that when code is pushed to `main` it's deployed to the development instance. When code is pushed to `prod` it's pushed to staging. 

To see more about branching and the deployment steps, see the [Branching](branching.md) page.

## Running a Django admin command

You can SSH into a running instance of the app. Running Django apps is a little more complicated on Cloud Foundry than running locally.

Don't forget to change the organization or space you need first with `cf target -o your_org_name` or `cf target -s your_space_name`

```shell
cf ssh {APP NAME}
cd app
export LD_LIBRARY_PATH=~/deps/0/python/lib
~/deps/0/python/bin/python manage.py {COMMAND WITH ARGS}
```
