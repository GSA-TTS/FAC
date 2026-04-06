# API Development

## Versions

Each version lives in its own folder. The API is a PostgREST server that stands up after our other main services and relies on our DB having certain elements applied to it already. On our main application startup the scripts within `api_standup.sh` will tear down and rebuild those elements (schemas, functions, and views). The "live" versions are determined in `api_versions.py`.

api_v1_1_0 is the default. The views match up with our dissemination tables.

api_v1_1_1 is the same as v1_1_0, but it includes the combined table. This was a hassle to implement, so it gets its own version.

api_v1_2_0 relies on the `audit` tables, rather than the `dissemination` ones. The results it provides are the same, but the views are generated differently due to the data source, and it is somewhat more performant.

## Comparing Results Between Versions

For some API changes, we expect nothing to be different between one version and the next.

reset; python compare_api_results.py --port 3000 --scheme http --api_base_1 localhost --api_base_2 localhost --api_version_1 api_v1_1_0 --api_version_2 api_v1_2_0 --endpoint general --environment local --start_date 2023-03-01 --end_date 2023-03-03 --any_order
