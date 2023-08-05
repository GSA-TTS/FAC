all: clean source_data build_xlsx format_jsonnet build_templates build_sections 
json: format_jsonnet build_templates build_templates

template_specs = $(wildcard source/excel/templates/*.jsonnet)
section_specs = $(wildcard source/sections/*.jsonnet)

xlsx = $(wildcard output/excel/xlsx/*-workbook*.xlsx)
json = $(wildcard output/excel/json/*.json)

source_data:
	python3 scripts/generate_lookup_schemas.py source/data/cfda-lookup-20230626.csv source/base/FederalProgramNames.json
	python3 scripts/generate_lookup_schemas.py source/data/cluster-names-20230626.csv source/base/ClusterNames.json

clean:
	for f in $(xlsx); do \
		rm $$f; \
	done
	for f in $(json); do \
		rm $$f; \
	done

build_xlsx: source_data
	for f in $(specs); do \
		python3 render.py $$f; \
	done

format_jsonnet:
	for jsonnet_file in $(template_specs); do \
		jsonnetfmt -i "$$jsonnet_file"; \
	done
	for jsonnet_file in $(section_specs); do \
		jsonnetfmt -i "$$jsonnet_file"; \
	done

build_template_json:
	for jsonnet_file in $(specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/excel/json/"$$base_name.json" "$$jsonnet_file"; \
	done

build_sections:
	for jsonnet_file in $(section_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/sections/"$$base_name.json" "$$jsonnet_file"; \
	done

build_templates: build_template_json
	for jsonnet_file in $(template_specs); do \
		echo "------------------------------"; \
		echo $$jsonnet_file; \
		echo "------------------------------"; \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		python3 scripts/render.py $$jsonnet_file output/excel/xlsx/"$$base_name.xlsx"; \
	done
	for jsonnet_file in $(template_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/excel/json/"$$base_name.json" "$$jsonnet_file"; \
	done
