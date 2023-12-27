import boto3
import os
import sys
from botocore.client import Config

def get_s3_client(env):
    if env == "census":
        prefix = "CENSUS_"
    elif env == "preview":
        prefix = "PREVIEW_"
    else:
        print("Invalid environment passed to get_s3_client. Exiting.")
        sys.exit(-1)

    s3 = boto3.client(
        service_name="s3",
        region_name=os.getenv(f"{prefix}AWS_DEFAULT_REGION"),
        aws_access_key_id=os.getenv(f"{prefix}AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv(f"{prefix}AWS_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4"),
    )
    return s3