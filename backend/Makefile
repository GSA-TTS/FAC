# Install python dependencies
install:
	@pip install -r requirements.txt

# Generate an updated requirements.txt
compile:
	@rm -f requirements*.txt
	@pip-compile --generate-hashes requirements.in

# Sync your local environment
sync:
	@pip-sync requirements*.txt
