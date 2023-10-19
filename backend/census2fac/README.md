# Census to FAC data migration

## Overview

This is implemented as a sjango app to leverage existing management commands and settings. It has python and shell scripts to

* load raw census data as csv files into an S3 bucket
* create postgres tables from these csv files
* perform any data clean up required to create a table from a csv file
* perforn any ither validations or cleansing, such as verifying the integrity of df files, of data coming into FAC from Census

## Infrastructure changes

* Create a new S3 bucket in cloud.gov spaces as well as in the ;ocal environment
** Affected files: TBD
* Create a new Postgres instance both in CG and locally
** Affected files:

## Utilities

* load_raw.py - Read zip files providd by Census, and upload them to the S3 bucket.
* zip2sql.py - Create postgres tables and poulate them using the contents of the csv files in the S3 bucket after cleansing them

## Pre-requisites for

* A django app that reads the tables created here as unmanaged models and populates SF-SAC tables by creating workbooks, etc to simulate a real submission
