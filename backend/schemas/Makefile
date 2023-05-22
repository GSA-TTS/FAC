specs = $(wildcard sources/*.jsonnet)

all:
	for jsonnet_file in $(specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o sections/"$$base_name.json" "$$jsonnet_file"; \
	done

build-json: all
