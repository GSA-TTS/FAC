# Development

We use [Django's test execution framework](https://docs.djangoproject.com/en/4.0/topics/testing/) along with select 3rd party packages to implement and execute tests for our python code.

## Contents

- [Development](#development)
  - [Contents](#contents)
  - [Packages](#packages)
  - [Running the tests](#running-the-tests)
  - [Writing new tests](#writing-new-tests)
  - [Testing Actions Locally](#testing-actions-locally)
  - [Coverage](#coverage)

## Packages
 - [model_bakery](https://model-bakery.readthedocs.io/en/latest/), to help create data and instances within our tests

## Running the tests

The test suite is run with Django's `test` management command. A number of helpful arguments and options are available, [check the Django docs for details.](https://docs.djangoproject.com/en/4.0/topics/testing/overview/#running-tests-1)

```shell
# Run the whole test suite
docker-compose run web python manage.py test

# Run only the tests within the `audit` app
docker-compose run web python manage.py test audit

# Run only the tests within the `audit.test_models` module
docker-compose run web python manage.py test audit.test_models

# Run only the tests within the `audit.test_models.SingleAuditChecklistTests` class
docker-compose run web python manage.py test audit.test_models.SingleAuditChecklistTests
```
We are configured to require 99% test coverage. If a file should not be counted for test coverage, it can be added to the `.coveragerc` file with an explanation. For example, we don't need tests for environment specific settings so that is added there.

## Writing new tests

We write tests for new and modified functionality specific to this project. A few examples:

We **do** write tests for:
* Classmethods on Django models implemented by us, like `__str__`

We **don't** write tests for:
* Asserting that `models.Charfield` checks the length of an incoming `string` against the `max_length` attribute

## Testing Actions Locally

[Act](https://github.com/nektos/act) can be used to run our Django testing workflow [test.yml](.github/workflows/test.yml) locally:

```shell
# Run act with the act_base platform
act test --platform ubuntu-latest=lucasalt/act_base:latest
```

## Accessibility

We're using [Lighthouse-ci](https://github.com/GoogleChrome/lighthouse-ci) for accessibility testing.

Accessibility tests are executed as part of our CI/CD pipeline on each PR to the `main` branch, commit to the `main` branch, and PR into the `prod` branch.

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
Then you can run the scan. Here is an example running a basic scan against our dev instance.
```
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
-t https://fac-dev.app.cloud.gov/
```

#### Bandit
We are using [bandit](https://bandit.readthedocs.io/en/latest/) for static code analysis of our python code.

Run this locally via docker:
```
 docker-compose run web bandit -r crt_portal/
```

Bandit tests are executed as part of our CI/CD pipeline on each PR to the `main` branch, commit to the `main` branch, and PR into the `prod` branch.
