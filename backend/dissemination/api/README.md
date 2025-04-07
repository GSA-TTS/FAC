# comparing API results between API versions

For some API changes, we expect nothing to be different between one version and the next.

reset; python compare_api_results.py --port 3000 --scheme http --api_base_1 localhost --api_base_2 localhost --api_version_1 api_v1_1_0 --api_version_2 api_v1_2_0 --endpoint general --environment local --start_date 2023-03-01 --end_date 2023-03-03 --any_order