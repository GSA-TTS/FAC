# Install python dependencies
install:
	@pip install -r requirements.txt

# Generate an updated requirements.txt
compile:
	@rm requirements.txt
	@pip-compile --generate-hashes ./requirements/requirements.in -o requirements.txt --allow-unsafe


# Generate an updated dev-requirements.txt
compile-dev:
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
	@bandit -r .
	@echo "mypy:"
	@mypy .

# Run Django tests:
test:
	@python -m coverage run --source="." manage.py test && coverage report -m --fail-under=99
