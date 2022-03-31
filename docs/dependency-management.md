# Dependency Management

We use [pip-tools](https://github.com/jazzband/pip-tools) to manage our python dependencies and create reproducible environments.

## Tools

* [pip-tools](https://github.com/jazzband/pip-tools) for dependency management

## Workflow

1. Our requirements are tracked in [../backend/requirements.in](../backend/requirements.in)
2. We use `pip-compile` to generate a `requirements.txt` file with hashes
3. We track both in version control
3. We use `requirements.txt` to install dependencies locally as well as in deployed environments.
