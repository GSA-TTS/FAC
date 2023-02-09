# Secrets

We use [encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) to store sensitive information and deploy automatically to cloud.gov.

## Contents

- [Secrets](#secrets)
  - [Contents](#contents)
  - [Tools](#tools)
  - [Repository Secrets](#repository-secrets)
  - [Cloud.gov Service Account](#cloudgov-service-account)
  - [SAM.gov API System Account](#samgov-api-system-account)
  - [Rotating Credentials](#rotating-credentials)
  - [Local Testing](#local-testing)

## Tools

* [Github Actions Site](https://github.com/features/actions)
* [FAC's actions](https://github.com/GSA-TTS/FAC/tree/main/.github/workflows)

## Repository Secrets

Locally, you should store all secrets in a `.env` file within the `/backend` directory. These will get added in to the Docker containers when they're built and launched.

Deployed secrets are stored in repository secrets located in the repository settings on Github. *Note that only an admin can add or remove repository secrets.*

## Cloud.gov Service Account

To deploy to cloud.gov automatically, we have a `space-deployer` [service account](https://cloud.gov/docs/services/cloud-gov-service-account/) that holds a service key with unique credentials.  

The service account credentials are stored in the repository secrets under:

- `CF_USERNAME`
- `CF_PASSWORD`

## SAM.gov API System Account

We use SAM.gov to look up information about the organizations that use the FAC. 

To use the SAM.gov API, you will need a key. A user API key can be created for local testing, but a [system account](https://www.fsd.gov/gsafsd_sp?id=gsafsd_kb_articles&sys_id=f8426db91b594d9006b09796bc4bcb52) system API key will be needed for the site when it's in production. 

To generate a SAM.gov user key, follow these steps:

1. Head to [SAM.gov](https://www.sam.gov/), then click "Sign In" in the top right corner.
1. You will be passed to Login.gov to authenticate. 
1. When you return, you may need to answer a few questions, but then you should have a basic account created.
1. Head to your [profile page](https://sam.gov/profile/details), and then under Public API Key, click the eyeball to reveal it or the rectangles icon to copy it.
1. Add `SAM_API_KEY = '<key>'` to your `.env` file (where `<key>` is your actual key from the page).
1. Rebuild/restart any open Docker containers you have going.

To generate a SAM.gov System Account API key, follow these steps:

1. Users registered with a non-government email address and associated with an entity OR users registered with a government email address may request a system account for public data access.
1. If a user satisfies the above registration criteria they will be able to access the System Accounts widget from their Workspace page after logging in.
1. The user can then select “Go to System Accounts” from the widget and fill out the required sections.
1. The requested system account will then need to be approved. After approval the user will be notified via email and they can also see the updated status in the System Account widget.
1. The user can select ‘Go to System Accounts’ again in the widget from their workspace and enter a new system account password.
1. After setting up the password the user will see a new section for retrieving a system account API Key.
1. The user must enter their password again to retrieve the key.

NOTE: To obtain access to the FOUO/Sensitive Entity API data with a system account the user must be registered with a government email address.

The system account API key will be stored as `SAM_API_KEY` in the repository secrets in Github.

## Rotating Credentials

The Cloud.gov service account and SAM.gov API Key credentials should be rotated every 90 days. 

To rotate credentials associated with a cloud.gov service key, follow the steps [here](https://cloud.gov/docs/services/cloud-gov-service-account/) to delete and recreate the service key.

```shell
cf delete-service-key my-service-account my-service-key
cf create-service-key my-service-account my-service-key
cf service-key my-service-account my-service-key
```

To rotate the API key associated with a SAM.gov system account, follow the steps [here](https://www.fsd.gov/sys_attachment.do?sys_id=5462e13d1b594d9006b09796bc4bcbd2) to delete and recreate the API key. You will need to update it in GitHub after this. Once updated, a new deploy will automatically replace it on the instance.

## Local Testing

[Act](https://github.com/nektos/act) can be used to test Github Actions locally and can handle secrets in `.secrets`.  

To test pushing to cloud.gov locally with the [deploy.yml](.github/workflows/deploy.yml) workflow:

1. `$ touch .secrets`
2. Create a [space-deployer service account](https://cloud.gov/docs/services/cloud-gov-service-account/) and copy the username and password into `.secrets` under `CF_USERNAME=` and `CF_PASSWORD=`.
3. Create a [system account API key](https://www.fsd.gov/sys_attachment.do?sys_id=5462e13d1b594d9006b09796bc4bcbd2) and copy the API key into `.secrets` under `SAM_API_KEY=`.
4. Run act: `$ act`
