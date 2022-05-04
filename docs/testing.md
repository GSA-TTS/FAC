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

We're using [Pa11y](https://pa11y.org/) for accessibility testing of interfaces rendered by the backend. Those interfaces are currently limited to Django's Admin Interface.

pa11y tests are defined in and may be executed from: `../pa11y_tests`

Accessibility tests are executed as part of our CI/CD pipeline on each commit to `main` and proposed merge into `main`. We're not currently _failing_ the build on reported errors but we will in the future.

To execute the tests locally, follow the general workflow defined in our [Github Action definitions](../.github/workflows/test.yml).
1. Start a development instance of the application
2. Ensure there's an account created with admin access
3. Install pa11y
4. Execute the pa11y tests with `npm run`

## Coverage

**TODO**
