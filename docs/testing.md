# Testing

We use [Django's test execution framework](https://docs.djangoproject.com/en/4.0/topics/testing/) along with select 3rd party packages to implement and execute tests for our python code.

## Contents

- [Testing](#testing)
  - [Contents](#contents)
  - [Packages](#packages)
  - [Running the tests](#running-the-tests)
  - [Writing new tests](#writing-new-tests)
  - [Testing Actions Locally](#testing-actions-locally)
  - [Accessibility](#accessibility)
  - [Security scans](#security-scans)
      - [OWASP ZAP](#owasp-zap)
      - [Bandit](#bandit)
  - [Linting](#linting)
- [End-to-end testing](#end-to-end-testing)
  - [Testing behind Login.gov](#testing-behind-logingov)

## Packages
 - [model_bakery](https://model-bakery.readthedocs.io/en/latest/), to help create data and instances within our tests

## Running the tests

The test suite is run with Django's `test` management command. A number of helpful arguments and options are available, [check the Django docs for details.](https://docs.djangoproject.com/en/4.0/topics/testing/overview/#running-tests-1)

```shell
# Run the whole test suite
docker compose run web python manage.py test

# Run only the tests within the `audit` app
docker compose run web python manage.py test audit

# Run only the tests within the `audit.test_models` module
docker compose run web python manage.py test audit.test_models

# Run only the tests within the `audit.test_models.SingleAuditChecklistTests` class
docker compose run web python manage.py test audit.test_models.SingleAuditChecklistTests
```
We are configured to require 90% test coverage. If a file should not be counted for test coverage, it can be added to the `.coveragerc` file with an explanation. For example, we don't need tests for environment specific settings so that is added there.

## Writing new tests

We write tests for new and modified functionality specific to this project. A few examples:

We **do** write tests for:
* Class methods on Django models implemented by us, like `__str__`

We **don't** write tests for:
* Asserting that the built-in `models.Charfield` checks the length of an incoming `string` against the `max_length` attribute

## Testing Actions Locally

[Act](https://github.com/nektos/act) can be used to run our Django testing workflow [test.yml](.github/workflows/test.yml) locally:

```shell
# Run act with the act_base platform
act test --platform ubuntu-latest=lucasalt/act_base:latest
```

## Accessibility
We use a combination of [Cypress](https://www.cypress.io/) and [Axe](https://www.deque.com/axe/) for accessibility (A11y) testing. 

<!-- TODO: Accessibility tests are executed as part of our CI/CD pipeline on each PR to the `main` branch, commit to the `main` branch, and PR into the `prod` branch. -->
Accessibility tests currently cover the full submission pipeline, the access management pages, and the search pages.
They should run in less than half a minute for baseline coverage.

To run accessibility tests locally, do the following:

Ensure `DISABLE_AUTH=True` in your local environment variables. This will mean the blank "test_user@test.test" will be used. 
You will not have to log in, do not need permissions to access pages, and the username in the top right will display strangely. 
But, Cypress also won't need any permissions or have to rely on Login.gov in any way.

"Log in" once (visit the app) to ensure the test user exists in your local environment.

Run the `load_fixtures` management command in your docker container, to ensure a submission of type "In Progress", "Ready for Certification", and "Accepted" exist for the test user. This will also load some dummy dissemination objects, so that at least one record will exist for search.
```shell
docker compose exec web /bin/bash  # Enter the docker shell
python manage.py load_fixtures     # Run the management command
```

Run `npm i` to ensure Cypress and its related dependencies are up-to-date.

Open Cypress with `npx Cypress open`, and run the `accessibility.cy.js` spec.

This can be done in headless mode via the command line with either of these two lines:
1. `npx cypress run --spec "cypress/e2e/accessibility.cy.js"`
2. `npm run test:a11y:cypress` (which in turn runs the above line).

## Security scans
#### OWASP ZAP
We're using the [OWASP ZAP baseline scan](https://github.com/marketplace/actions/owasp-zap-baseline-scan) in GitHub actions. We have a config file in the workflows folder that governs pass or fail for each test.

Triggers for these scans:
 - Scan the dev instance after deploying to dev
 - Scan the dev instance before deploying to staging
 - Scan the staging instance before deploying to prod
 - Scan the prod instance after deploying to prod

To run locally, pull the container:
```
docker pull owasp/zap2docker-stable
```
Then you can run the scan. Here is an example running a basic scan against our dev instance. This is being run from the top level folder.
```
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
-t https://fac-dev.app.cloud.gov/ -c zap.conf
```

#### Bandit
We are using [bandit](https://bandit.readthedocs.io/en/latest/) for static code analysis of our python code.

Run this locally via docker:
```
 docker compose run web bandit -r crt_portal/
```

Bandit tests are executed as part of our CI/CD pipeline on each PR to the `main` branch, commit to the `main` branch, and PR into the `prod` branch.

## Linting

We use a variety of linters on the project:

* flake8 - error and style checker
* Black - code formatter
* mypy - type annotation checker
* djlint - HTML formatter and linter
* eslint - JS static code analysis and linter
* stylelint - CSS linter

You can run most of them directly after installing the app's dependencies (i.e. `black .`).

You can also run most of them as one command with `make lint`.

Like with Bandit, new code will need to pass all of these to be merged into the `main` branch.

# End-to-end testing

We use Cypress to do end-to-end testing of the application. Tests are defined
in files in [backend/cypress/e2e/](/backend/cypress/e2e). To run these tests:
- Run the app. Then, from the `FAC/backend` directory:
- `npm ci`
- [Create a testing login.gov account](https://github.com/GSA-TTS/FAC/blob/main/docs/testing.md#testing-behind-logingov)
- [Set up the fac() alias](https://github.com/GSA-TTS/FAC/blob/main/docs/development.md?plain=1#L125)
- [Generate a new JWT](https://github.com/GSA-TTS/FAC/blob/main/backend/dissemination/README.md#creating-a-jwt-secret)
- `CYPRESS_LOGIN_TEST_EMAIL='<your email>' CYPRESS_LOGIN_TEST_PASSWORD='<your  password>' CYPRESS_LOGIN_TEST_OTP_SECRET='<your otp>' CYPRESS_LOGIN_TEST_EMAIL_AUDITEE='<auditee email*>' CYPRESS_LOGIN_TEST_PASSWORD_AUDITEE='<auditee password*>' CYPRESS_LOGIN_TEST_OTP_SECRET_AUDITEE='<auditee otp*>' CYPRESS_API_GOV_JWT='<your jwt>' CYPRESS_API_GOV_URL='localhost:3000' CYPRESS_API_GOV_USER_ID_ADMIN='<admin user uuid**>' CYPRESS_ADMIN_API_VERSION='<current admin api version***>' npx cypress open`
	- Note: All of this goes on one line
	- *: These fields can be found in the [FAC dev keys Google doc](https://docs.google.com/spreadsheets/d/1byrBp16jufbiEY_GP5MyR0Uqf6WvB_5tubSXN_mYyJY/edit#gid=0)
	- **: This field can be the UUID associated with any of the [users with administrative privileges](https://github.com/GSA-TTS/FAC/blob/main/backend/support/api/admin_api_v1_0_0/create_access_tables.sql)
	- ***: This current value for this field can be found [here](https://github.com/GSA-TTS/FAC/blob/1af236093cab16beb783eec4021b162f04c90840/backend/docker-compose.yml#L112)
- Click `E2E Testing`
- Select `Chrome` and click `Start E2E Testing in Chrome`

## Testing behind Login.gov

 For tests that run against our existing Cloud.gov environments, we can't use
 our `DISABLE_AUTH` environment variable to allow the end-to-end tests access
 to our authenticated pages. Instead, we need to use an actual Login.gov
 sandbox account to log in.

 We have a Google Group <fac-gov-test-users@gsa.gov> to provide an email
 address for those test users. Additional test users can be created using that
 email address with different values after a plus sign, e.g.
 <fac-gov-test-users+staging@gsa.gov>.

 When creating a new Login.gov sandbox account with an email address of that
 form, after confirming the email address in the email that was sent to the
 Google Group, create a random password and record it locally, ideally in a
 KeePassXC password vault. When the account creation flow asks to set up a
 second factor, choose "Authentication Application". On the next screen where
 you would normally use a QR code to configure an authenticator application,
 there is a text box with a secret key labeled "enter this code manually into
 your authentication app". You need to save that secret key alongside the
 password.

 To pass that email address, password, and secret key into Cypress, set the
 environment variables `CYPRESS_LOGIN_TEST_EMAIL`, `CYPRESS_LOGIN_TEST_PASSWORD`, and
 `CYPRESS_LOGIN_TEST_OTP_SECRET`. You'll need similar credentials for
 `CYPRESS_LOGIN_TEST_EMAIL_AUDITEE`, `CYPRESS_LOGIN_TEST_PASSWORD_AUDITEE`, and
 `CYPRESS_LOGIN_TEST_OTP_SECRET_AUDITEE`. These can be the same values, but ideally
 they'll belong to a different account. Obviously, do not store these values in our
 Github repository. To use them in a Github Actions workflow, use the [Github
 Actions secrets
 store](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
