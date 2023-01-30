# Data loading

We have a script to load the public data.

Download data from https://facdissem.census.gov/PublicDataDownloads.aspx
Then unzip the files and place the them in data_distro/data_to_load/

Load them locally with: `manage.py public_data_loader`

It's a lot of data, so you might just want to run it against one of the cloud.gov instances. You can do that with task here is [an example](https://github.com/GSA-TTS/FAC/blob/main/backend/manifests/task-manifest-staging.yaml)


We are doing an initial data load in February 2022. There will be another round of data upload when we get the private data from Census and a mapping to the PDF files of reports. We will need to update data before launch to grab any records that have been added since the initial download work.

The upload script should be flexible enough to handle changes in the models that may happen between data loads.

To refresh the data loading script:
1) Look at the `make_table_structure` function in uploadmapping.py. Make sure things like new_fields are up to date.
2) Rerun the `make_table_structure` function to get a new `upload_mapping`. You can run this using `manage.py shell` and just grab the contents that it prints to console.
3) Check the outputs to make sure that things make sense. You will need to do a manual check on the upload mapping, If a data column needs to go to more than one model, that needs to be addressed in the upload script. For example, AUDITOR_EIN has the same info reported on two of the upload tables, so you only need to upload it once.
4) Check the `public_data_loader` script. Renaming should mostly be handled by `upload_mapping` but changing relationships need to be accounted for in the script. Make sure the relationships that are in the `add_relational` output of `make_table_structure` are added in the script.

