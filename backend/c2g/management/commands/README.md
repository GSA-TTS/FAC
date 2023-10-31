# load_csv_from_s3

The load_csv_from_s3 script expects CSVs to be in the S3 bucket. It uses Pandas to load the CSV into a dataframe (chunking at 10,000 rows), and then loads those rows into the Postgres database via Django models representing the raw Census data. By using Pandas, we correctly handle multi-line data, and can (if necessary) do additional modifications to the data.

We should avoid pre-processing the data at this stage. 

## Assumptions

The underlying assumption is that there is a CSV in a bucket that we have permissions to access.

It is assumed this can be run manually (locally or by SSHing into an instance) or via GH Action.

## Usage

```
  fac load_csv_from_s3 --bucket <bucket-name> --object <filename>
```

There are optional parameters. 

`--chunksize`. This lets us read large CSVs by iterating through them.

```
  fac load_csv_from_s3 --bucket <bucket-name> --object <filename> --chunksize 10
```

The default value for `--chunksize` is 10000.

## Loading all the data

To load all the data, a local, command-line script is provided.

```
load-all-census-csvs.bash <local-directory> <remote-path>
```

This script will look in a local directory containing Census CSVs. It assumes they will be named

    ELECAUDITFINDINGS.csv
    ELECAUDITHEADER.csv
    ...

It will then use the Minio client `mc` to load each of these files into your local Minio instance. 

The remote path allows you to chose where the files will go. For example

```
load-all-census-csvs.bash ~/data census-files/
```

will look for the data in your home directory in a folder called `data`, and load them into the bucket `fac-c2g-s3` to the path(s)

census-files/ELECAUDITFINDINGS.csv
census-files/ELECAUDITHEADER.csv
...


After copying the files into Minio, it then loads the files into the local Postgres instance using `load_csv_from_s3`

```
fac load_csv_from_s3 --bucket fac-c2g-s3 --object census-files/ELECAUDITFINDINGS.csv
fac load_csv_from_s3 --bucket fac-c2g-s3 --object census-files/ELECAUDITHEADER.csv
...
```



## That's it

After running the script, all the raw data files are loaded into the database, and are ready for further processing.




