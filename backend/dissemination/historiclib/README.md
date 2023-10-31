# historiclib

Added a `historiclib`.

In it are directories, one per workbook. There is also a `common`
directory.

Each directory contains files, one per field that we are mapping.

The files should be named for the source column and destination named
range. For example

uei-to-uei.py

Use hyphens around the `to`. Use underscores elsewhere (e.g. in the
named range).

The file should contain a single function named the same as the file.

These functions consume a single value, and return a single value.

The functions might raise a `MigrationMappingError`. 

That error should be caught further up, and indicate that a workbook migration failed.

The SUGGESTION comments in `excel_creation.py` show some places this might be used. It can also be used in the `FieldMap` structures as the transformation function that is included in each of those structures. 

I would recommend not using `str` as a mapping function; instead, in `common`, create a `string_to_string` function that does a no-op. Why? For debugging purposes. We may later discover we need to instrument or otherwise do something in the case of those transforms, and being able to debug there will be useful.

(For example, if we have character set issues, making sure we pass all strings to a common function lets us fix this for all workbooks easily.)
