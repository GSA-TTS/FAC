SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON=${SYSTEM_PYTHON}

all: clean merge_aln_csvs source_data build_xlsx format_jsonnet build_templates build_sections build_audit_json

json: format_jsonnet build_templates build_templates build_audit_json

template_specs = $(wildcard source/excel/templates/*.jsonnet)
section_specs = $(wildcard source/sections/*.jsonnet)
audit_specs = $(wildcard source/audit/*.jsonnet)
base_specs = $(wildcard source/base/*.jsonnet)

xlsx = $(wildcard output/excel/xlsx/*-workbook*.xlsx)
json = $(wildcard output/excel/json/*.json)

merge_aln_csvs:
	@echo "Merging and cleaning ALNs CSV files..."
	@${PYTHON} scripts/merge_aln_csvs.py
	@echo "Merged CSV generated successfully."

source_data:
	@echo "Generating lookup schemas..."
	@${PYTHON} scripts/generate_lookup_schemas.py cfda-lookup source/base/FederalProgramNames.json
	@${PYTHON} scripts/generate_lookup_schemas.py cluster-names source/base/ClusterNames.json

clean:
	@echo "Cleaning up output files..."
	for f in $(xlsx); do \
		rm $$f; \
	done
	for f in $(json); do \
		rm $$f; \
	done
	@echo "Cleanup complete."

build_audit_json:
	@echo "Building audit JSON files..."
	for jsonnet_file in $(audit_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/audit/"$$base_name.json" "$$jsonnet_file"; \
	done

build_xlsx: source_data
	@echo "Building XLSX files..."
	for f in $(specs); do \
		${PYTHON} render.py $$f; \
	done

format_jsonnet:
	@echo "Formatting JSONNET files..."
	for jsonnet_file in $(template_specs); do \
		jsonnetfmt -i "$$jsonnet_file"; \
	done
	for jsonnet_file in $(section_specs); do \
		jsonnetfmt -i "$$jsonnet_file"; \
	done

build_template_json:
	@echo "Building template JSON files..."
	for jsonnet_file in $(specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/excel/json/"$$base_name.json" "$$jsonnet_file"; \
	done

build_sections:
	@echo "Building sections..."
	for jsonnet_file in $(section_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/sections/"$$base_name.json" "$$jsonnet_file"; \
	done

build_templates: build_template_json
	@echo "Building templates..."
	for jsonnet_file in $(template_specs); do \
		echo "------------------------------"; \
		echo $$jsonnet_file; \
		echo "------------------------------"; \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		${PYTHON} scripts/render.py $$jsonnet_file output/excel/xlsx/"$$base_name.xlsx"; \
	done
	for jsonnet_file in $(template_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/excel/json/"$$base_name.json" "$$jsonnet_file"; \
	done

build_base_schemas:
	@echo "Building base schemas..."
	for jsonnet_file in $(base_specs); do \
		base_name=$$(basename "$$jsonnet_file" .jsonnet); \
		jsonnet -o output/base/"$$base_name.json" "$$jsonnet_file"; \
	done
