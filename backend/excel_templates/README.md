### Developing rendered XLSX docs

This needs to be worked into a module/command in the Django framework, and we need some improved/integrated tests.

The Makefile helps a bit

make venv
make deps
make all

To get rid of the XLSX outputs

make clean

It should be the case you can run

`pytest`

in the `excel_templates` folder and it will "just work." Meaning it will run a test to try and walk the schemas and sheets, and determine if they all have the same named ranges.