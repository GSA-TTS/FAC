import boto3
import os
import sys
from botocore.client import Config
from botocore.client import ClientError
from uuid import uuid4

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

# Upload the file to S3
# s3_client.upload_file('hello.txt', 'MyBucket', 'hello-remote.txt')

def get_client_and_bucket(location):
    if location == "census":
        s3 = get_s3_client("census")
        bucket_name = os.getenv("CENSUS_BUCKET_NAME")
    if location == "preview":
        s3 = get_s3_client("preview")
        bucket_name = os.getenv("PREVIEW_BUCKET_NAME")
    return (s3, bucket_name)

def s3_download(location, destination_path, source_key):
    try:
        client, bucket_name = get_client_and_bucket(location)
        temp_filename = str(uuid4())
        print(f"- downloading {source_key} to {temp_filename}")
        client.download_file(bucket_name, source_key, os.path.join(destination_path, temp_filename))
        return temp_filename
    except Exception as e:
        print(f"- Download failed. {e}")
        return False

def s3_upload(location, source_file, destination_key):
    try:
        client, bucket_name = get_client_and_bucket(location)
        print(f"- uploading {source_file} to {destination_key}")
        client.upload_file(source_file, bucket_name, destination_key)
        return True
    except Exception as e:
        return False

def s3_copy(d, live_run=False):
    local_temp = d["local_temp_path"]
    source_env = d["source_env"]
    source_file = d["source_file"]
    destination_env = d["destination_env"]
    destination_file = d["destination_file"]

    print(f"Copying [is_live? {live_run}]\n\tFROM {source_file}\n\tTO   {destination_file}")
    if live_run:
        # census = get_s3_client(source_env)
        # preview = get_s3_client(destination_env)
        temp_filename = s3_download(source_env, local_temp, source_file)
        # If the download failed, don't continue.
        if not temp_filename:
            return False
        if destination_env == "local":
            print(f"Renaming to {destination_file}")
            os.rename(os.path.join(local_temp, temp_filename), 
                    destination_file)
            return True
        else:
            s3_upload(destination_env, os.path.join(local_temp, temp_filename), destination_file)
            retval = None
            if s3_check_exists(destination_env, destination_file):
                print("- SUCCESS")
                retval = True
            else:
                print("- UPLOAD FAILED")
                retval = False
            os.remove(os.path.join(local_temp, temp_filename))
            return retval

    
def s3_check_exists(location, key):
    s3, bucket_name = get_client_and_bucket(location)
    try:
        ho = s3.head_object(
            Bucket = bucket_name,
            Key = key
        )
        return True
    except ClientError as ce:
        return False
