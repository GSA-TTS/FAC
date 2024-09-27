# sling

Point to the DB

```
export PG='postgresql://postgres@localhost:5432/postgres?sslmode=disable'
```

This gives me the general table as a CSV to STDOUT:

```
sling run --src-conn $PG --src-stream 'public.dissemination_general' --stdout
```

With a configuration file (YAML):

`config1.yaml`:

```
source: postgresql://postgres@localhost:5432/postgres?sslmode=disable
target: LOCAL

defaults:
  target_options:
    format: csv

streams:
  public.dissemination_general:
    object: file:///tmp/dg.csv

  public.dissemination_federalaward:
    object: file:///tmp/dfa/*.csv
    target_options:
        file_max_rows: 100000
```

and then

```
sling run -r config1.yaml
```
