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

def s3_copy(d, live_run=False):
    local_temp = d["local_temp_path"]
    source_env = d["source_env"]
    source_file = d["source_file"]
    destination_env = d["destination_env"]
    destination_file = d["destination_file"]

    print(f"Copying \n\tFROM {source_file}\n\tTO   {destination_file}")
    if live_run:
        census = get_s3_client(source_env)
        preview = get_s3_client(destination_env)

    
