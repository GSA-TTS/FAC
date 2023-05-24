specs = $(wildcard source/sections/*.jsonnet)

all:
	for jsonnet_file in $(specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/sections/"$$base_name.json" "$$jsonnet_file"; \
	done

build-json: all