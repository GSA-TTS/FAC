# Install python dependencies
install:
	@pip install -r requirements.txt

# Generate an updated requirements.txt
compile:
	@rm requirements.txt
	@pip-compile --generate-hashes ./requirements/requirements.in -o requirements.txt --allow-unsafe

# Sync your local environment
sync:
	@pip-sync requirements.txt
