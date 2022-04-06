# Development

We use [Django's test execution framework](https://docs.djangoproject.com/en/4.0/topics/testing/) along with select 3rd party packages to implement and execute tests for our python code.


## Contents

* [Packages](#packages)
* [Running-the-tests](#running-the-tests)
* [Coverage](#coverage)


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


## Coverage

**TODO**
