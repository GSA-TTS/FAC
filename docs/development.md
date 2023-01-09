# Development

We use either [Docker with `docker-compose`](#docker) or [local development](#local-development) when working on issues and shipping pull requests.

## Contents

* [Tools](#tools)
* [Setting up your dev environment](#setting-up-your-dev-environment)
  * [Environment Variables](#environment-variables)
  * [Docker](#docker)
  * [Local Development](#local-development)
* [Django setup](#django-setup)
* [Python code quality tooling](#python-code-quality-tooling) 

## Tools

* [Docker](https://docker.com)
* Local dev
  * [Pyenv](https://github.com/pyenv) for managing Python versions
  * [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for managing virtual environments
  * [Postgres](https://www.postgresql.org/)
  * [SAM.gov](https://sam.gov/content/home) to validate UEI's

## Setting up your dev environment

---
**NOTE**

Target python version is defined in [../backend/runtime.txt](../backend/runtime.txt)

---

## Environment Variables

Create a .env file in the `/backend` directory.
Add and define the following environment variables using the instructions below.

```
ENV = 'LOCAL'
SAM_API_KEY =
SECRET_KEY =
SECRET_LOGIN_KEY =
```

If you need to add these to your local environment (should end up in `~/.bash_profile`, `~/.bashrc`, `~/.zshrc`, or whatever flavor of shell you're using.)

#### SAM_API_KEY
We use the `SAM_API_KEY` environment variable to interact with the SAM.gov API.
To test UEI validation using the SAM.gov API with a personal API key, follow these steps on (https://SAM.gov):

* Registered users can request for a public API on ‘Account Details’ page. This page can be accessed here: [Account Details page on SAM.gov](https://sam.gov/profile/details)
* Users must enter their password on ‘Account Details’ page to view the API Key information. If an incorrect password is entered, an error will be returned.
* After the API Key is generated on ‘Account Details’ page, the API Key can be viewed on the Account Details page immediately. The API Key is visible until users navigate to a different page.
* If an error is encountered during the API Key generation/retrieval, then users will receive an error message and they can try again.

#### SECRET_KEY
Generate a random secret key for local development.

#### SECRET_LOGIN_KEY
The `DJANGO_SECRET_LOGIN_KEY` environment variable is used to interact with Login.gov. For local development, you have three options:
*  (Recommended) If you wish to use the shared Login.gov sandbox client application and credentials, you can obtain a valid  `DJANGO_SECRET_LOGIN_KEY` from our shared [dev secrets document](https://docs.google.com/spreadsheets/d/1byrBp16jufbiEY_GP5MyR0Uqf6WvB_5tubSXN_mYyJY/edit#gid=0)
*  If you wish to use the shared Login.gov sandbox client application, but create your own client credentials, you must first be granted access to the GSA-FAC Login.gov sandbox team. Once you can access the GSA-FAC client application, follow [Login.gov's documentation for creating a public certificate](https://developers.login.gov/testing/#creating-a-public-certificate). Once created, you can add the newly-generated public key to the GSA-FAC app, and set `DJANGO_SECRET_LOGIN_KEY` to the base64-encoded value of the corresponding private key.
*  If you wish to use your own Login.gov sandbox client application, follow [Login.gov's documentation for setting up a test application](https://developers.login.gov/testing/). Once completed, open `settings.py` and set `OIDC_PROVIDERS.login.gov.client_registration.client_id` so that it matches the `issuer` string for your newly-created client application. NOTE: changes to the `client_id` should __not__ be checked into version control!

## Docker

An application and database are configured in [../backend/docker-compose.yml](../backend/docker-compose.yml), we create a volume to persist the development database, and we mount our `./backend` working directory to the `web` container so that changes made in development are reflected in the container without needing to re-build.

1. Install Docker
2. Build and start using [../backend/docker-compose.yml](../backend/docker-compose.yml)

    ```shell
    # with a working directory of ./backend
    docker-compose build
    docker-compose up
    ```

3. The application will start and be accessible @ http://localhost:8000/


## Local Development
### Install the tools

`brew install pyenv pyenv-virtualenv`

If your tools are previously installed, you may need to

`brew update && brew upgrade pyenv`

to have all of the most recent versions of Python available. This could be slow if you haven't updated in a while. Get a cup of ☕.

(Your setup process on Windows/Linux will vary. Currently, we assume local development in a Linux-like environment.)

### Update your environment

You will likely need to [update your shell](https://stackoverflow.com/questions/33321312/cannot-switch-python-with-pyenv).

```
eval "$(pyenv init --path)"
```

should end up somewhere in `~/.bash_profile`, `~/.bashrc`, or whatever flavor of shell you're using.

### Set link flags

You *might* need to set link flags. Otherwise, when you `make install`, there could be failures in the building of `psycog2`. YMMV.

```
export LDFLAGS="-L/usr/local/opt/openssl/lib -L/usr/local/lib -L/usr/local/opt/expat/lib" && export CFLAGS="-I/usr/local/opt/openssl/include/ -I/usr/local/include -I/usr/local/opt/expat/include" && export CPPFLAGS="-I/usr/local/opt/openssl/include/ -I/usr/local/include -I/usr/local/opt/expat/include"
```

### Create a virtual environment

You may need to install the Python version being used by the team. The following take place in the `backend` directory of the checked out repository.

```
FAC_PYTHON_VERSION=`cat .python-version`
pyenv install $FAC_PYTHON_VERSION
```

You may run into a `pyenv` mismatch between the version in `.python-version` and possible versions `pyenv` supports, for example, `.python-version` might contain `3.10` but `pyenv` only allows `3.10.0` or other minor versions of `3.10`. One approach to fixing this is to create a symlink in `~/.pyenv/versions` pointing a `3.10` symlink at whatever installed version you prefer. A command to do this might look like `ln -s ~/.pyenv/versions/3.10.1 ~/.pyenv/versions/3.10`.

Then, set up the virtualenv.

`pyenv virtualenv $FAC_PYTHON_VERSION FAC`

### Activate your new virtual environment

`pyenv activate FAC`

Depending on how you feel about seeing the virtualenv in your prompt:

```
pyenv-virtualenv: prompt changing will be removed from future release. configure `export PYENV_VIRTUALENV_DISABLE_PROMPT=1' to simulate the behavior.
```

### Install python dependencies

```
python -m pip install --upgrade pip
pip install pip-tools
```

### Django environment variables

We use environment variables to configure much of how Django operates, at a minimum you'll need to configure the uri of your local database.

Set a `DATABASE_URL` environment variable with the uri of your local database
    *  `postgresql://[userspec@][hostspec][/dbname]`


### Django setup

In development, you'll need to run Django's `manage.py` and specific commands like `makemigrations`, `createsuperuser`, and more.

If developing with Docker, execute these commands from within the `web` container


```shell
docker-compose run web python manage.py $COMMAND $ARGS
```

As a convenience, you can create an alias in your shell following this or a similar pattern
```shell
fac ()
{
  docker-compose run web python manage.py ${@}
}
```

**Example workflows**

Let's use this workflow to create a `superuser` in our development environment so we can access the Admin interface!


```shell
# Start our docker containers w/ docker-compose
docker-compose up

# Django management command to create a new superuser
docker-compose run web python manage.py createsuperuser

# Follow the prompts to enter username, password, etc.

# Enter the user/pass @ the Admin login page
open http://localhost:8000/admin
```

### Python code quality tooling

The tests (plus coverage report) can be run locally with `make test`.

The linting/formatting/security scanning/type checking can be run all together locally with `make lint`.

#### Testing

We use the Django native test framework plus [coverage.py](https://coverage.readthedocs.io/).

The tests and the coverage report are run as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml). Minimum test coverage is currently set at 99%, an arbitrarily-chosen value.

#### Linting

We use [Flake8](https://github.com/PyCQA/flake8) for linting. Because Flake8 runs `pylint` for us, configuration is effectively in two files: [backend/.flake8](https://github.com/GSA-TTS/FAC/blob/main/backend/.flake8) for Flake-specific settings and [backend/pyproject.toml](https://github.com/GSA-TTS/FAC/blob/main/backend/pyproject.toml) for `pylint`-specific settings.

The settings are mostly default, with the main exception being line length. We depart from the PEP-8 standard and instead use the `black` [default of 88](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#line-length), and have altered the Flake8 settings to match this.


In addition, in using `black` we follow the [suggestion of disabling the `E203` error](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#slices) because of inconsistencies around treatment of the slice operator.

There are some opinionated enabled/disabled `pylint` messages in [backend/pyproject.toml](https://github.com/GSA-TTS/FAC/blob/main/backend/pyproject.toml) that we will revisit over time if they prove problematic.

Linting is checked as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml).

#### Formatting

As stated, we use [black](https://black.readthedocs.io/en/stable/index.html) with the default settings for formatting.

Formatting is checked as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml), and will fail if code is not formatted as `black`  expects it to be.

#### Security scanning

We use [bandit](https://bandit.readthedocs.io/en/latest/) for automated security scans, and run it with default settings.

Security scanning is checked as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml).

#### Type checking

We use [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking. We currently configure it (in  [backend/pyproject.toml](https://github.com/GSA-TTS/FAC/blob/main/backend/pyproject.toml)) to [ignore missing imports](https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports) because type annotation support for Django isn't yet mature.

Type checking is done as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml).
