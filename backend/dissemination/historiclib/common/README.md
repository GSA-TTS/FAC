# common functions

The functions in this directory are common to multiple historic tables.

For example, `uei.py` contains code for validating and migrating UEIs. It is used in the generation of multiple workbooks.

In `notes_to_sefa`, we put functions used only in the migration of notes_to_sefa workbooks.

Each file should map just one value or column. In this way, we might expect a number of functions for the federal awards workbook, but very few for the notes_to_sefa workbook.

In this way, debugging the migration becomes easier. We know exactly where the code for all transformation lies.
