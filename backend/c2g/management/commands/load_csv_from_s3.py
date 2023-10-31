from django.core.management.base import BaseCommand
import boto3
from io import BytesIO
from django.conf import settings
from botocore.client import ClientError, Config
import logging
# We are potentially going to run into issues with large CSVs.
# A fix for this would be to use Dask. It automatically/internally
# partitions large dataframes.
# https://www.coiled.io/blog/dask-read-csv-to-dataframe
# import dask.dataframe as dd
import pandas as pd

from c2g.models import (
    ELECAUDITFINDINGS,
    ELECAUDITHEADER,
    ELECAUDITS,
    ELECCAPTEXT,
    ELECCPAS,
    ELECEINS,
    ELECFINDINGSTEXT,
    ELECNOTES,
    ELECPASSTHROUGH, 
    ELECUEIS,
)

models = [
    ELECAUDITFINDINGS,
    ELECAUDITHEADER,
    ELECAUDITS,
    ELECCAPTEXT,
    ELECCPAS,
    ELECEINS,
    ELECFINDINGSTEXT,
    ELECNOTES,
    ELECPASSTHROUGH, 
    ELECUEIS,
]

logger = logging.getLogger(__name__)

## 
# CONTRACT : string string -> BytesIO
# Loads a CSV from a bucket and returns
# a BytesIO representation of that file.
def load_file_from_s3(bucket, object_name):
    s3 = boto3.client(
        service_name="s3",
        region_name=settings.AWS_S3_PRIVATE_REGION_NAME,
        aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_PRIVATE_INTERNAL_ENDPOINT,
        config=Config(signature_version="s3v4"),
    )
    file = BytesIO()
    
    try:
        s3.download_fileobj(bucket, object_name, file)
    except ClientError:
        logger.error("Could not download {}".format(object_name))
        return None
    
    # Seek to the start of the file.
    file.seek(0)
    return file

## CONTRACT : string -> model
# Consumes a string and checks to see if the name of 
# a model appears in the object name.
def get_model_from_object_name(object_name):
    for m in models:
        if m.__name__ in object_name:
            return m
    return None

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--bucket", type=str, required=True)
        parser.add_argument("--object", type=str, required=True)
        parser.add_argument("--chunksize", type=int, required=False, default=10000)
         

    def handle(self, *args, **options):  # noqa: C901
        bucket = options["bucket"]
        object = options["object"]
        chunksize = options["chunksize"]

        # Load the object as a bytestream.
        # In Python, this is file-like.
        bytesio = load_file_from_s3(bucket, object)
        # Exit if it did not load.
        if bytesio is None:
            logger.error("BytesIO object is None; could not load.")
            return -1

        # Get the right model for this file
        the_model = get_model_from_object_name(object)
        if the_model is None:
            logger.error(f"Could not find a model for {object}.")
            return -1

        # Pandas neatly handles multi-line values in columns, etc.
        # If we want to read everything all at once, it looks like this:
        # df = pd.read_csv(bytesio)
        # But, we want to chunk the read.
        for df in pd.read_csv(bytesio, iterator=True, chunksize=chunksize):            
            # Delete all the data first. For some tables, the DBKEY/AUDITYEAR
            # are not unique. Therefore, we cannot delete while loading.
            for _, row in df.iterrows():
                # Start by deleting with the same DBKEY and AUDITYEAR.
                # Every model has them.
                objects = the_model.objects.all().filter(DBKEY=row["DBKEY"], AUDITYEAR=row["AUDITYEAR"])
                for o in objects:
                    o.delete()
        
        # Go back to the start of the BytesIO object so we can read it again.
        bytesio.seek(0)

        # This is painful. We go through the chunks twice.
        for df in pd.read_csv(bytesio, iterator=True, chunksize=chunksize):       
            # Each row is a dictionary. The columns are the 
            # correct names for our model. So, this should be a 
            # clean way to load the model from a row.
            for _, row in df.iterrows():
                obj = the_model(**row)
                obj.save()
