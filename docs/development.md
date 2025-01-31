# Development

We use either [Docker with `docker compose`](#docker) or [local development](#local-development) when working on issues and shipping pull requests.

See [the pull request template](../.github/pull_request_template.md) for steps to follow when submitting or reviewing pull requests.

## Contents

* [Tools](#tools)
* [Setting up your dev environment](#setting-up-your-dev-environment)
  * [Windows Setup](#windows-setup)
  * [Environment Variables](#environment-variables)
  * [Docker](#docker)
  * [Local Development](#local-development)
* [Development in principle](#development-in-principle)
* [Python code quality tooling](#python-code-quality-tooling) 
* [Frontend code quality tooling](#frontend-code-quality-tooling) 

## Tools

* [Python](https://www.python.org/)
  * Target python version is defined in [../backend/runtime.txt](../backend/runtime.txt).
* [Docker](https://docker.com)
* [Node.js](https://nodejs.org/en/download/package-manager) for end-to-end testing with Cypress.
* [CF8](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) for access to the cloud.gov CLI.
* [Postgres](https://www.postgresql.org/)
* [SAM.gov](https://sam.gov/content/home) to validate UEI's
### Local Development Tools
  * [Pyenv](https://github.com/pyenv) for managing Python versions
  * [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for managing virtual environments
#### Additional Windows Tools (Optional)
Windows users *may* need the following tools installed in addition to the above tools.
* [GNU Make](https://www.gnu.org/software/make/) - For running Makefile commands.
* [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) OR [Git Bash](https://gitforwindows.org/) - Provides a Unix-like shell environment.
* [Visual Studio Code (VS Code)](https://code.visualstudio.com/) - install extensions for WSL and Remote Development.
* [Chocolatey](https://chocolatey.org/install) - a package manager that will allow for installation of tools that are not available on Windows, such as GNU make (used for running Makefile operations).
  * Here is an example of how you would use Chocolatey in the terminal to install GNU make:
    ```
    choco install make
    ```

  * If make doesn’t run in Git Bash, prepend commands with winpty, e.g.:
    ```
    winpty make all
    ```
---

## Setting up your dev environment

### EditorConfig

We have a `.editorconfig` file at the root directory with basic settings.
See [editorconfig.org](https://editorconfig.org/) for more information.

---

**NOTE** - For Windows developers

By default, your IDE will acknowledge `CRLF` as the denotation for newlines. Many scripts in this repository **require** `LF` denotation (noticeably the .sh files when you first try to run and test the application). Make sure your IDE uses `LF` denotation for newlines when reading through each of these scripts.

You can use the Git commands below BEFORE cloning the repository to your local computer to prevent files from using `CRLF` by default. If you've already cloned it with incorrect line endings, you should reclone the repository.
```
# don't use --global if you only want this behavior for a specific repository.
git config --global core.autocrlf false
# this ensures all files use LF.
git config --global core.eol lf

# If the repo was cloned before setting this, reclone it:
rm -rf your-repo
git clone https://github.com/your-org/your-repo.git
```



---

### Windows Setup
#### **Option 1: Use WSL**

1. Install **WSL** and Ubuntu:
   ```powershell
   wsl --install -d Ubuntu
   ```
2. Install **Visual Studio Code** and the **Remote - WSL** extension.
3. Open Ubuntu in VS Code by running:
   ```bash
   code .
   ```
4. Inside WSL Ubuntu, install dependencies:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-venv python3-pip make build-essential
   ```
5. Install **Pyenv** and **Pyenv-Virtualenv** (Recommended for managing Python versions):
   ```bash
   curl https://pyenv.run | bash
   ```
   Follow the instructions to update `.bashrc` or `.zshrc`.

#### **Option 2: Use Git Bash**

1. Install **Git for Windows**.
2. Install **Chocolatey** and run:
   ```powershell
   choco install make
   ```
3. Install Python and dependencies manually.
4. Use Git Bash for commands but expect potential compatibility issues.

### **Windows-Specific Git Settings**

By default, Windows uses **CRLF line endings**, which can cause issues when running shell scripts. Before cloning the repo, run:

```bash
git config --global core.autocrlf false
git config --global core.eol lf
```

## Activating Your Development Environment

### **1. Clone the Repository**

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo/backend
```

### **2. Set Up Python Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate  # (Linux/macOS, WSL)
source venv/Scripts/activate  # (Windows Git Bash)
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Verify Development Tools**

```bash
python --version  # Should match the target version
make --version    # Ensure GNU Make is installed
```

---
### Environment Variables

Create a .env file in the `/backend` directory.
Add and define the following environment variables using the instructions below.

```
ENV = 'LOCAL'
DISABLE_AUTH = False
SECRET_KEY = YourSecretKey
SAM_API_KEY = 
DJANGO_SECRET_LOGIN_KEY = 
LOGIN_CLIENT_ID = 
```

#### ENV
The `ENV` environment variable specifies the set of configuration settings to use while running. For local development, it should be `LOCAL`, which will enable settings that should work on your local machine with Docker.

On our Dev/Staging/Production environments, it will be set to `DEVELOPMENT`/`STAGING`/`PRODUCTION` respectively. Setting it to one of these will turn on configuration it's expecting while deployed to Cloud.gov.

In GitHub Actions and our CI/CD pipeline, it is set to `TESTING`.  It will enable settings expected to make unit tests complete properly while still trying to emulate a Cloud.gov situation.

While you **could** change this, you generally shouldn't need to.

#### DISABLE_AUTH
The `DISABLE_AUTH` variable tells Django to disable the Login.gov authorization. This should almost always be `False` unless you need to temporarily disable it for your local development. 

In the Dev/Staging/Production environments, it will be set to `False` and require all users to go to Login.gov to log in.

In GitHub Actions (the CI/CD pipeline), it will be set to `True` to complete unit testing and frontend testing properly.

#### SECRET_KEY
Create your own secret key for local development. Django uses this to provide cryptographic signing.

#### SAM_API_KEY
We use the `SAM_API_KEY` environment variable to interact with the SAM.gov API.
To test UEI validation using the SAM.gov API with a personal API key, follow these steps on (https://SAM.gov):

* (Recommended) If you wish to use the shared API key, you can obtain a valid `SAM_API_KEY` from our shared [dev secrets document](https://docs.google.com/spreadsheets/d/1byrBp16jufbiEY_GP5MyR0Uqf6WvB_5tubSXN_mYyJY/edit#gid=0).
* Registered users can request for a public API on ‘Account Details’ page. This page can be accessed here: [Account Details page on SAM.gov](https://sam.gov/profile/details)
* Users must enter their password on ‘Account Details’ page to view the API Key information. If an incorrect password is entered, an error will be returned.
* After the API Key is generated on ‘Account Details’ page, the API Key can be viewed on the Account Details page immediately. The API Key is visible until users navigate to a different page.
* If an error is encountered during the API Key generation/retrieval, then users will receive an error message and they can try again.

#### DJANGO_SECRET_LOGIN_KEY
The `DJANGO_SECRET_LOGIN_KEY` environment variable is used to interact with Login.gov. For local development, you have three options:
*  (Recommended) If you wish to use the shared Login.gov sandbox client application and credentials, you can obtain a valid  `DJANGO_SECRET_LOGIN_KEY` from our shared [dev secrets document](https://docs.google.com/spreadsheets/d/1byrBp16jufbiEY_GP5MyR0Uqf6WvB_5tubSXN_mYyJY/edit#gid=0).
*  If you wish to use the shared Login.gov sandbox client application, but create your own client credentials, you must first be granted access to the GSA-FAC Login.gov sandbox team. Once you can access the GSA-FAC client application, follow [Login.gov's documentation for creating a public certificate](https://developers.login.gov/testing/#creating-a-public-certificate). Once created, you can add the newly-generated public key to the GSA-FAC app, and set `DJANGO_SECRET_LOGIN_KEY` to the base64-encoded value of the corresponding private key.
*  If you wish to use your own Login.gov sandbox client application, follow [Login.gov's documentation for setting up a test application](https://developers.login.gov/testing/). Once completed, open `settings.py` and set `OIDC_PROVIDERS.login.gov.client_registration.client_id` so that it matches the `issuer` string for your newly-created client application. NOTE: changes to the `client_id` should __not__ be checked into version control!

#### LOGIN_CLIENT_ID
The `LOGIN_CLIENT_ID` environment variable is our unique application identifier at Login.gov. Each environment has its own client ID. You can obtain the client ID that should be used during local development from our shared [dev secrets document](https://docs.google.com/spreadsheets/d/1byrBp16jufbiEY_GP5MyR0Uqf6WvB_5tubSXN_mYyJY/edit#gid=0)

---
For local testing, you may need to specify a few other variables:
* The clamav-rest service looks at port `9000` by default - which is already in use. You can change this to a different port if preferred by using `CLAMAV_PORT = {new port number}`.
* Cypress variables for running local end-to-end tests. See the [testing docs](https://github.com/GSA-TTS/FAC/blob/main/docs/testing.md#end-to-end-testing) for more.

If you need to add these to your local environment (should end up in `~/.bash_profile`, `~/.bashrc`, `~/.zshrc`, or whatever flavor of shell you're using.)

---

### Docker

We **STRONGLY** recommend you use Docker for development and testing as it enables the fastest and easiest set up of all of the components you need to get up and running quickly.

An application and database are configured in [../backend/docker-compose.yml](../backend/docker-compose.yml), we create a volume to persist the development database, and we mount our `./backend` working directory to the `web` container so that changes made in development are reflected in the container without needing to re-build.

#### Checklist

1. Install Docker
2. Build and start using [../backend/docker-compose.yml](../backend/docker-compose.yml)

    ```shell
    # with a working directory of ./backend
    docker compose build
    docker compose up
    ```

3. The application will start and be accessible @ http://localhost:8000/. The following statements **should** appear at the bottom of your shell output:

    ```shell
    web-1         | Starting development server at http://0.0.0.0:8000/
    web-1         | Quit the server with CONTROL-C.
    ```

    To confirm that everything is running properly, you can check the state of each image in the stack through the shell or Docker Desktop. Every image except for `historic-data` should be running by the time the application starts.

#### Setting up the stack

Once you have the stack running, you will want to run commands against it to further configure your environment for development and testing. Specifically, you'll need to run Django's `manage.py` and specific commands like `makemigrations`, `createsuperuser`, and more.

You'll need to run your commands *inside* the container, which you can either do with `docker compose`, or you can do by `exec`ing into the container and running them directly. Each has benefits and tradeoffs, and your specific needs will dictate which you do.

To run via `compose`:

```shell
docker compose run web python manage.py $COMMAND $ARGS
```

As a convenience, you can create an alias in your shell following this or a similar pattern:

```shell
fac ()
{
  docker compose run web python manage.py ${@}
}
```

Alternatively, you can connect to the running instance and run the tests from it, which has significantly less overhead:

```shell
docker compose exec web /bin/sh
```

That gives you a shell from which you can run, for example:

```shell
python manage.py test
```

Now, you're ready to start doing some work.

#### Running migrations

Although the migrations are run automatically, try running the migrations. This should not fail on a clean build. You will need to do this before you do anything else.


```shell
docker compose run web python manage.py makemigrations
```

```shell
docker compose run web python manage.py migrate
```

#### Staticfiles

Files that fall under the `/backend/static` directory need to be collected into the untracked directory `/backend/staticfiles`. This is done automatically when docker comes up, so you will 
likely not need to do anything with these.

However, if you edit any files in `/backend/static` you will need to either re-up docker or manually collect static. This is done via `python manage.py collectstatic`.

Try to avoid pushing frequent edits to files in `/backend/static` (more than once every few days), as each change causes a rebuild of the ghcr image for use in the automatic PR tests.

#### Load SingleAuditChecklist fixtures

You can load fake fixture data for single audit checklists. There is a list
of users in
[`backend/users/fixtures/user_fixtures.py`](/backend/users/fixtures/user_fixtures.py)
that will be created by default. If you are a new developer, you can add your
information in that file so that there will be a user created for you if
necessary and various submission fixtures available to that user. You will need your
Login.gov sandbox UUID to specify as your "username". The easiest way to get that is to
log in while running in a local Docker environment and look for the message that says something like

```
INFO Successfully logged in user b276a5b3-2d2a-42a3-a078-ad57a36975d4
```

Once you have a user listed in that file, you can run the command

```shell
docker compose run web python manage.py load_fixtures
```

It is not completely obvious that you would want to, but you could run this in
one of the Cloud.gov environments with `cf run-task` like

```shell
cf run-task ENVIRONMENT --command "./manage.py load_fixtures" --name fixtures
```

You can also run this command for users by email address(es). These users do
not have to be present in
[`backend/users/fixtures/user_fixtures.py`](/backend/users/fixtures/user_fixtures.py),
but must have logged into the system in order for this to work.

```shell
docker compose run web python manage.py load_fixtures userone@example.com usertwo@example.com
```

This will create a fake submission for each of the users. These submissions
will be separate for each user—this command only associates one user with each
fake submission.

Note that all of these fake submissions use the same UEI.

#### Run tests

If everything is set up correctly, you should now be able to run tests. You will want to make sure that your `.env` is set so that auth is not diabled.

```
DISABLE_AUTH = False
```

Once you do that, run the stack in one shell:

```shell
docker compose up
```

and in another shell, run the tests:

```shell
docker compose run web python manage.py test
```

#### The short version

The above steps are the bare minimum. To reduce the likelihood of errors, you can also do the following in the `backend` directory:

```
make docker-clean
make docker-first-run
make docker-test
```

The `Makefile` makes clear what these do. In short, the first command builds the container (in case there are changes), runs migrations, loads test data, and creates the S3 mock bucket. The second runs tests.

#### Full cleanup

When switching branches, working with migrations, or generally trying to move between versions of the application, you will likely find that a full cleanup of your docker environment is important.

```
docker compose down --volumes
docker system prune -f
docker volume prune -f
make docker-clean
make docker-first-run
```

It is possible, after many starts and stops, to end up filling your docker volumes. This sequence removes *everything*, and gives you a clean docker state. It is likely that doing this *at least once per day* is a good idea. When switching between branches to test features (especially features involving changes to models) it is a good idea to do a full clean before switching branches and launching the stack locally.

#### Adding data and users

If you want to move past the test data, it is possible to download previous years' data and load it locally. This is important for dissemination API development and dissemination API testing.

#### Adding users

Let's use this workflow to create a `superuser` in our development environment so we can access the Admin interface! However, you will need to first log in to the local environment using your sandbox login.gov account; if the user does not exist in the system, it cannot be promoted to a superuser or staff user.

The best way to create a login.gov user is to run [http://localhost:8000](http://localhost:8000) click on the log in link from your app running locally. (It needs to be localhost and not http://0.0.0.0:8000 to work with how we configured our Login.gov test account.) 

Follow the instructions on the Login.gov test site to set up an account.

Then, log into the site using login.gov. This will create a user but that user won't have privlages.

You can promote your user account to have superuser status by using our custom management command. While the stack is running (it had to be, in order to login and create your user):

```shell
# Django management command to promote a user to be a superuser
docker compose run web python manage.py make_super email@address
docker compose run web python manage.py make_staff email@address
```

Now, you can open [http://localhost:8000/admin](http://localhost:8000/admin) in your browser. (Use local host and not 0.0.0.0, to work with local login.gov auth.)


#### Doing a clean set of tests

If you want to take everything back to a squeaky-clean start, you'll need to get rid of some things.

First, bring everything down.

```
docker compose down
```

Then, remove the containers.

```
docker rm -f $(docker ps -a -q)
```

Then, the volumes.

```shell
docker volume rm $(docker volume ls -q)
```

Now, you'll need to rebuild.

```shell
docker compose build
```

and then up.

```shell
docker compose up
```

---
**NOTE** - the above commands are also available through the Makefile: 

```
make docker-clean
```

At this point, you'll need to re-run migrations, load test, and recreate your test bucket before you can run tests. Or, you can re-run

```
make docker-first-run
make docker-test
```
---

#### What to do if your local tests fail

The most likely explanation is that one of the services (such as MinIO or ClamAV) didn’t finish startup before the tests reached a point that was reliant on that service.

The easiest way to handle this is to run `docker compose up` and wait for ClamAV and Django to start, then run tests in another shell.

The most efficient way to run tests is to run them in the same container, via something like:

```sh
docker compose exec web /bin/bash -c "python manage.py test; /bin/bash"
```

If any of the services (with the exception of `historic-data`) are not running or have erroneous looking outputs after running `docker compose up`, revisit [the above instructions](#setting-up-your-dev-environment) to make sure that all the steps have been followed.

## Development, in principle

We're working against a [QASP](https://derisking-guide.18f.gov/qasp/) (which does *not* look like the linked document, but it serves as an example), and therefore we have a variety of practices we are holding ourselves to.

Many of these run on every commit as part of our Github actions workflows.

### Python code quality tooling

The tests (plus coverage report) can be run locally with `make test`.

The linting/formatting/security scanning/type checking can be run all together locally with `make lint`.

---

### Testing

We use the Django native test framework plus [coverage.py](https://coverage.readthedocs.io/).

The tests and the coverage report are run as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml). Minimum test coverage is currently set at 90%.

---

### Linting

We use [Flake8](https://github.com/PyCQA/flake8) for linting. Because Flake8 runs `pylint` for us, configuration is effectively in two files: [backend/.flake8](https://github.com/GSA-TTS/FAC/blob/main/backend/.flake8) for Flake-specific settings and [backend/pyproject.toml](https://github.com/GSA-TTS/FAC/blob/main/backend/pyproject.toml) for `pylint`-specific settings.

The settings are mostly default, with the main exception being line length. We depart from the PEP-8 standard and instead use the `black` [default of 88](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#line-length), and have altered the Flake8 settings to match this.


In addition, in using `black` we follow the [suggestion of disabling the `E203` error](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#slices) because of inconsistencies around treatment of the slice operator.

There are some opinionated enabled/disabled `pylint` messages in [backend/pyproject.toml](https://github.com/GSA-TTS/FAC/blob/main/backend/pyproject.toml) that we will revisit over time if they prove problematic.

Linting is checked as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml).

#### Additional linters
We use `djlint` to lint html template files. When developing locally:
* Use `djlint --reformat <path_to_html_files>` to format the files. 
* Use the `--lint` option to get a list of linter errors.

---

### Formatting

As stated, we use [black](https://black.readthedocs.io/en/stable/index.html) with the default settings for formatting.

Formatting is checked as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml), and will fail if code is not formatted as `black`  expects it to be.

---

### Security scanning

We use [bandit](https://bandit.readthedocs.io/en/latest/) for automated security scans, and run it with default settings.

Security scanning is checked as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml).

---

### Type checking

We use [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking. We currently configure it (in  [backend/pyproject.toml](https://github.com/GSA-TTS/FAC/blob/main/backend/pyproject.toml)) to [ignore missing imports](https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports) because type annotation support for Django isn't yet mature.

Type checking is done as a GitHub action, configured in [.github/workflows/test.yml](https://github.com/GSA-TTS/FAC/blob/main/.github/workflows/test.yml).

---

### Frontend code quality tooling

We use [stylelint](https://stylelint.io/) to lint and format CSS/SCSS. Configuration is located in [backend/.stylelintrc.json](https://github.com/GSA-TTS/FAC/blob/main/backend/.stylelintrc.json), but mostly just imports the standard configs: `stylelint-config-standard` and `stylelint-config-standard-scss`.

To lint and format JavaScript, we use [eslint](https://eslint.org/). eslint configuration lives in [backend/.eslintrc](https://github.com/GSA-TTS/FAC/blob/main/backend/.eslintrc).

These tools run automatically as a part of our CI workflow in GitHub actions, but to run these tools locally to check formatting or automatically fix formatting errors before committing, just run: `npm run check-all` or `npm run fix-all`, respectively.

---

## Local Development

You _can_ run the application locally, however, we **STRONGLY** recommend using the Docker method above instead ([here](#docker)). It will work locally, but you will need to manually install and configure the components. Not every scenario may be covered. Be warned! This method requires **PostgreSQL** and additional setup. See [local-development.md](local-development.md) for additional warnings and details. 

---
## Troubleshooting

### **Common Issues**

#### **"ModuleNotFoundError" for Python Packages**

- Ensure the virtual environment is activated (`source venv/bin/activate`).
- Reinstall dependencies: `pip install -r requirements.txt`.

#### **"Command Not Found" for Make**

- If using **Git Bash**, install GNU Make via Chocolatey:
  ```powershell
  choco install make
  ```
- If using **WSL**, install it via Ubuntu:
  ```bash
  sudo apt install make
  ```

#### **"jsonnetfmt: command not found"**

- Ensure `jsonnet` is installed:
  ```bash
  sudo apt install jsonnet
  ```

#### **"ModuleNotFoundError: No module named '\_jsonnet'"**

- Install it manually:
  ```bash
  pip install --no-binary :all: pyjsonnet
  ```

#### **Docker Permission Issues**

- If you get permission errors when running Docker, add yourself to the Docker group:
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker
  ```
If using Windows, ensure that WSL 2 integration is enabled in Docker Desktop > Settings > Resources > WSL Integration.

#### **Error: Docker Daemon Not Running**

- If using Docker Desktop, ensure it is running before executing any docker commands.
  
---
