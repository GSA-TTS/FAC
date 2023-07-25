# workbook-generator

## The spirit/concept of the thing

The spirit of this spike was the following:

1. We have an ETL process that (arguably) needs (valid, populated) workbooks as input.
2. As output, the ETL processes puts data in dissemination tables.
3. Instead of checking if the data is in the dissemination tables, a regression/E2E test for the data would be to make API calls that extract the data.
4. If you have the data in your hands when you generate the workbook, you could *also* generate test tables to drive regression tests.

Meaning:

1. If we spit out populated workbooks, and 
2. A set of testing tables that say "*this* endpoint should produce *this* data"

All driven off of data we believe to be good, then we have a way of generating multiple, populated test cases.

### Possible gravy

1. To test cross-validation, we can use sets of workbooks output by the tool. In theory, they should all validate.
2. We can take sets of workbooks, and manually introduce errors that we know will produce cross-validation errors. These can then become part of a regression suite for cross-validation.

In other words, the goal was to quickly explore a test-data-creator.


## Running the tool

```
python main.py --dbkey <dbkey>
```

E.g.

```
python main.py --dbkey 100010
```

will generate two files (at the moment) in `output`. 

For now, only one-and-a-bit workbooks are generated. I started with federal awards, being the largest workbook. Note that data sometimes has to be pulled from multiple database tables to assemble a single workbook... and, some of our identifiers are new/different, so there's some reverse mapping/generation that has to be done in order to create new-style workbooks from old-style data. 

But, I think it's still better than trying to create test workbooks by hand.

## Requirements

1. In `data`, place the file `allfac22.sqlite3`. This is currently hard-coded into `models.py`. For now/for the spike, 2022 data should be plenty.
2. In `templates`, place recent workbook template files. Their names are also hard-coded into the script. If we change the workbook names (which, in theory, we're going to, to add version numbers...) this will break. If we keep this tool, we can be smarter about this.
3. The directory `output` will be created by the script.

The sqlite file can be found in our GDrive.

## Notes

All of the data in the SQLite file is, as far as we know, guaranteed to be public. The SQLite file was generated from the pipe-delimited CSVs that Census distributes on their website. So, it is data that Census published, and we converted from CSV to SQLite. 

The `models.py` file was generated with the `pwiz` tool. It is part of the `peewee` suite of tools that are associated with that (small?) Python ORM.

Something like

```
pwiz allfac22.sqlite3 > models.py
```

generated the file.

## And...

This is a spike. It can be thrown away. Or, it might have value. YMMV.