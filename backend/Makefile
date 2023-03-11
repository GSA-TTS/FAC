# Install python dependencies
install:
	@pip install -r requirements.txt
	@npm i

# Generate an updated requirements.txt
compile:
	@touch requirements.txt
	@rm requirements.txt
	@pip-compile --generate-hashes ./requirements/requirements.in -o requirements.txt --allow-unsafe

compile-assets:
	@node build-assets.js

# Generate an updated dev-requirements.txt
compile-dev:
	@touch dev-requirements.txt
	@rm dev-requirements.txt
	@pip-compile --generate-hashes ./requirements/dev-requirements.in -o dev-requirements.txt --allow-unsafe

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

# Run Django tests:
test:
	@python -m coverage run --source="." manage.py test && coverage report -m --fail-under=90

# Run Django tests with no coverage and with scoping
# e.g. just the audit/test_models.py tests:
#     make nctest fac.test.scope=audit.test_models"
# or all tests with no coverage:
#     make nctest
nctest:
	@python -m coverage run --source="." manage.py test ${fac.test.scope}
