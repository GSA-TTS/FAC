import boto3
from subprocess import (
    check_output,
    CalledProcessError,
    STDOUT
)

def get_s3_prefixes_from_config(config):
    parts = config.get("minio", "prefixes")
    lop = parts.split(",")
    lop = list(map(lambda s: s.strip(), lop))
    return lop

def create_s3_buckets(_, env, buckets):
    for bucket in buckets:
        try:
            check_output(["mc", "mb", f"myminio/{bucket}"],
                         env=env, stderr=STDOUT)
        except CalledProcessError as cpe:
            if "succeeded" not in str(cpe.output):
                print(cpe.output)

def make_s3_resource(config):
    s3 = boto3.resource('s3',
                        endpoint_url=config.get("minio", "endpoint"),
                        aws_access_key_id=config.get("minio", "user"),
                        aws_secret_access_key=config.get("minio", "pass"),
                        aws_session_token=None,
                        config=boto3.session.Config(signature_version='s3v4'),
                        verify=False
                        )
    return s3
