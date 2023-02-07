# Dependency Management

We use [pip-tools](https://github.com/jazzband/pip-tools) to manage our python dependencies and create reproducible environments.

## Tools

* [pip-tools](https://github.com/jazzband/pip-tools) for dependency management

## Workflow

1. Our requirements are tracked in [../backend/requirements.in](../backend/requirements.in)
2. We use `pip-compile` to generate a `requirements.txt` file with hashes
3. We track both in version control
4. We use `requirements.txt` to install dependencies locally as well as in deployed environments.

## Installing dependencies

If you are running the Docker containers, they will automatically install.

If you are running locally, you can run:

```bash
cd backend
pip install -r requirements.txt
```

for the dependencies for the project. Developer dependencies (like linters) can be installed with:

```bash
cd backend
pip install -r dev-requirements.txt
```
