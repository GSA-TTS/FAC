# Dependency Management

We use [pip-tools](https://github.com/jazzband/pip-tools) to manage our python dependencies and create reproducible environments.

## Tools

* [pip-tools](https://github.com/jazzband/pip-tools) for dependency management

## Workflow

1. Our requirements are tracked in [../backend/requirements](../backend/requirements)
2. We use `pip-compile` to generate a `requirements.txt` file with hashes
3. We track both in version control
4. We use `requirements.txt` to install dependencies locally as well as in deployed environments.
5. To avoid architecture-related complications, it's recommended to first exec into a Docker container before running the compilation:
  - `docker compose exec web /bin/bash`
  - `python -m piptools compile --allow-unsafe --generate-hashes --output-file=requirements.txt ./requirements/requirements.in`

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
