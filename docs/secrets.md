# Secrets

We use [encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) to store sensitive information and deploy automatically to cloud.gov.

## Contents

- [Secrets](#secrets)
  - [Contents](#contents)
  - [Tools](#tools)
  - [Repository Secrets](#repository-secrets)
  - [Service Account](#service-account)
  - [Rotating Credentials](#rotating-credentials)
  - [Local Testing](#local-testing)

## Tools

* [Github Actions](https://github.com/features/actions)

## Repository Secrets

Secrets are stored in repository secrets located in the repository settings on Github.

*Note that only an admin can add or remove repository secrets.*

## Service Account

To deploy to cloud.gov automatically, we have a `space-deployer` [service account](https://cloud.gov/docs/services/cloud-gov-service-account/) that holds a service key with unique credentials.  

The service account credentials are stored in the repository secrets under:

- `CF_USERNAME`
- `CF_PASSWORD`

## Rotating Credentials

The service account credentials should be rotated every 90 days. 

To rotate credentials associated with a service key, follow the steps [here](https://cloud.gov/docs/services/cloud-gov-service-account/) to delete and recreate the service key.

```shell
cf delete-service-key my-service-account my-service-key
cf create-service-key my-service-account my-service-key
cf service-key my-service-account my-service-key
```

## Local Testing

[Act](https://github.com/nektos/act) can be used to test Github Actions locally and can handle secrets in `.secrets`.  

To test pushing to cloud.gov locally with the [deploy.yml](.github/workflows/deploy.yml) workflow:

1. `$ touch .secrets`
2. Create a [space-deployer service account](https://cloud.gov/docs/services/cloud-gov-service-account/) and copy the username and password into `.secrets` under `CF_USERNAME=` and `CF_PASSWORD=`.
3. Run act: `$ act`
