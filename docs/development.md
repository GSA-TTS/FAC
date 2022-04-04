# Development

We use either Docker with `docker-compose` or local development when working on issues and shipping pull requests.
## Contents

* [Tools](#tools)
* [Setting up your dev environment](#python)
  * [Docker]()
  * [Local Development]()

## Tools

* Docker
* Local dev
  * [Pyenv](https://github.com/pyenv) for managing Python versions
  * [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for managing virtual environments
  * [Postgres](https://www.postgresql.org/)

## Setting up your dev environment

---
**NOTE**

Target python version is defined in [../backend/runtime.txt](../backend/runtime.txt)

---

### Docker

An application and database are configured in [../backend/docker-compose.yml](../backend/docker-compose.yml), we create a volume to persist the development database, and we mount our `./backend` working directory to the `web` container so that changes made in development are reflected in the container without needing to re-build.

1. Install Docker
2. Build and start using [../backend/docker-compose.yml](../backend/docker-compose.yml)

    ```shell
    # with a working directory of ./backend
    docker-compose build
    docker-compose up
    ```

3. The application will start and be accessible @ http://localhost:8000/


### Local Development

1. Install the tools listed above for your equipment
2. Use [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) to create a virtual environment
3. Activate your new virtual environment
4. Install python dependencies

    ```
    pyenv virtualenv <python version> FAC
    pyenv activate FAC
    pip install pip-tools
    make install
    ```
5. Set a `DATABASE_URL` environment variable with the uri of your local database
    *  `postgresql://[userspec@][hostspec][/dbname]`
