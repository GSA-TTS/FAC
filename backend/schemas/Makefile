SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON=${SYSTEM_PYTHON}

all: clean source_data build_xlsx format_jsonnet build_templates build_sections build_audit_json

json: format_jsonnet build_templates build_templates build_audit_json

template_specs = $(wildcard source/excel/templates/*.jsonnet)
section_specs = $(wildcard source/sections/*.jsonnet)
audit_specs = $(wildcard source/audit/*.jsonnet)
base_specs = $(wildcard source/base/*.jsonnet)

xlsx = $(wildcard output/excel/xlsx/*-workbook*.xlsx)
json = $(wildcard output/excel/json/*.json)

# New merged-csv target
merged-csv:
	@echo "Merging and standardizing CSV files..."
	$(PYTHON) -c " \
	import os, pandas as pd, glob; \
	folder = './source/data/ALNs_raw_downloads'; \
	output_file = './source/data/cfda-lookup-$(shell date +%Y%m%d).csv'; \
	print(f'Looking for CSV files in: {folder}'); \
	csv_files = glob.glob(f'{folder}/*.csv'); \
	print(f'CSV files found: {csv_files}'); \
	if not csv_files: \
	    print('No data found in the input files.'); \
	    exit(1); \
	all_data = []; \
	for f in csv_files: \
	    try: \
	        df = pd.read_csv(f, encoding='utf-8'); \
	    except UnicodeDecodeError: \
	        print(f'Warning: Could not read {f} with UTF-8. Trying ISO-8859-1.'); \
	        df = pd.read_csv(f, encoding='ISO-8859-1'); \
	    all_data.append(df); \
	combined_data = pd.concat(all_data, ignore_index=True); \
	column_mapping = { \
	    'Title': 'Program Title', \
	    'Assistance Listings Number': 'Program Number', \
	    'Date Published': 'Date Published', \
	    'Department/Ind. Agency': 'Department/Ind. Agency', \
	    'Funded': 'Funded', \
	    'Last Date Modified': 'Last Date Modified', \
	    'POC Information': 'POC Information', \
	    'Related Federal Assistance': 'Related Federal Assistance', \
	    'Sub-Tier': 'Sub-Tier', \
	    'Types of Assistance': 'Types of Assistance' \
	}; \
	combined_data = combined_data.rename(columns=column_mapping); \
	print(f'Saving merged and standardized CSV to: {output_file}'); \
	combined_data.to_csv(output_file, index=False, encoding='utf-8'); \
	print('CSV processing completed successfully.');"

source_data: merged-csv
	$(PYTHON) scripts/generate_lookup_schemas.py cfda-lookup source/base/FederalProgramNames.json
	$(PYTHON) scripts/generate_lookup_schemas.py cluster-names source/base/ClusterNames.json

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
