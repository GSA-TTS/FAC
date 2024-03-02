SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON=${SYSTEM_PYTHON}

all:  clean source_data build_xlsx format_jsonnet build_templates build_sections build_audit_json
json: format_jsonnet build_templates build_templates build_audit_json


template_specs = $(wildcard source/excel/templates/*.jsonnet)
section_specs = $(wildcard source/sections/*.jsonnet)
audit_specs = $(wildcard source/audit/*.jsonnet)
base_specs = $(wildcard source/base/*.jsonnet)

xlsx = $(wildcard output/excel/xlsx/*-workbook*.xlsx)
json = $(wildcard output/excel/json/*.json)

source_data:
	python scripts/generate_lookup_schemas.py source/data/cfda-lookup-20230626.csv source/base/FederalProgramNames.json
	python scripts/generate_lookup_schemas.py source/data/cluster-names-20230626.csv source/base/ClusterNames.json

clean:
	for f in $(xlsx); do \
		rm $$f; \
	done
	for f in $(json); do \
		rm $$f; \
	done

build_audit_json: 
	for jsonnet_file in $(audit_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/audit/"$$base_name.json" "$$jsonnet_file"; \
	done

build_xlsx: source_data
	for f in $(specs); do \
		python render.py $$f; \
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
		python scripts/render.py $$jsonnet_file output/excel/xlsx/"$$base_name.xlsx"; \
	done
	for jsonnet_file in $(template_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/excel/json/"$$base_name.json" "$$jsonnet_file"; \
	done

build_base_schemas:
	for jsonnet_file in $(base_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/base/"$$base_name.json" "$$jsonnet_file"; \
	done