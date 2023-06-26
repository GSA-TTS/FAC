specs = $(wildcard source/sections/*.jsonnet)

all:
	for jsonnet_file in $(specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/sections/"$$base_name.json" "$$jsonnet_file"; \
	done


source-data:
	python scripts/generate_lookup_schemas.py source/data/cfda-lookup-20230626.csv source/base/FederalProgramNames.json

build-json: all