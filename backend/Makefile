# Generate an updated requirements.txt
# We want these to run at the same time if we are ever updating a package in either file
# since the dev-requirements.txt are built on top of the requirements.txt
compile:
	@pip-compile --generate-hashes ./requirements/requirements.in -o requirements.txt --allow-unsafe
	@pip-compile --generate-hashes ./requirements/dev-requirements.in -o dev-requirements.txt --allow-unsafe

# Install python dependencies
install:
	@pip install -r requirements.txt
	@npm ci

compile-assets:
	@node build-assets.mjs

# Install python dev dependencies
install-dev:
	@pip install -r dev-requirements.txt

# Sync your dev environment
sync:
	@pip-sync dev-requirements.txt

# Run the linters
lint:
	@echo "Flake8:"
	@flake8
	@echo "black:"
	@black --check .
	@echo "bandit:"
	@bandit -c pyproject.toml -r .
	@echo "mypy:"
	@mypy .
	@echo "djlint:"
	@djlint .
	@echo eslint
	@npx eslint

# Run Django tests:
test:
	@python -m coverage run --source="." manage.py test --parallel && coverage report -m --fail-under=90

# Run Django tests with no coverage and with scoping
# e.g. just the audit/test_models.py tests:
#     make nctest fac.test.scope=audit.test_models"
# or all tests with no coverage:
#     make nctest
nctest:
	@python -m coverage run --source="." manage.py test --parallel ${fac.test.scope}

docker-first-run:
	docker compose build
	docker compose run web bash -c '\
		python manage.py makemigrations &&\
		python manage.py migrate'

docker-migrate:
	docker compose run web bash -c '\
		python manage.py makemigrations &&\
		python manage.py migrate'

# Run Django tests with docker
docker-test:
	docker compose build
	docker compose run web python manage.py migrate
	docker compose run web bash -c 'coverage run --parallel-mode --concurrency=multiprocessing manage.py test --parallel && coverage combine && coverage report -m --fail-under=90'

# Run Django tests with docker with no coverage and with scoping
# e.g. just the audit/test_models.py tests:
#     make nctest fac.test.scope=audit.test_models"
# or all tests with no coverage:
#     make nctest
docker-nctest:
	docker compose build
	docker compose run web python manage.py migrate
	docker compose run web python manage.py test --parallel ${fac.test.scope}

docker-lint:
	docker compose build
	docker compose run web bash -c 'flake8 && black --check . && bandit -c pyproject.toml -r . && mypy . && djlint .'

ghcr-first-run:
	docker compose -f docker-compose-web.yml run web python manage.py makemigrations
	docker compose -f docker-compose-web.yml run web python manage.py migrate
	docker compose -f docker-compose-web.yml run web python manage.py loaddata

# Run Django tests with docker
ghcr-test:
	docker compose -f docker-compose-web.yml run web python manage.py migrate
	docker compose -f docker-compose-web.yml run web bash -c 'coverage run --parallel-mode --concurrency=multiprocessing manage.py test --parallel && coverage combine && coverage report -m --fail-under=90'

# Run Django tests with docker with no coverage and with scoping
# e.g. just the audit/test_models.py tests:
#     make nctest fac.test.scope=audit.test_models"
# or all tests with no coverage:
#     make nctest
ghcr-nctest:
	docker compose -f docker-compose-web.yml run web python manage.py migrate
	docker compose -f docker-compose-web.yml run web python manage.py test --parallel ${fac.test.scope}

ghcr-lint:
	docker compose -f docker-compose-web.yml run web bash -c 'flake8 && black --check . && bandit -c pyproject.toml -r . && python -m pip install types-pytz && mypy . && djlint .'

docker-clean:
	docker compose down
	docker rm -f $(shell docker ps -a -q)
	docker volume rm $(shell docker volume ls -q)

docker-full-clean:
	rm -f .coverage.*
	docker compose down
	docker rm -f $(docker ps -a -q)
	docker volume rm $(docker volume ls -q)
	docker system prune -f
	docker volume prune -f
