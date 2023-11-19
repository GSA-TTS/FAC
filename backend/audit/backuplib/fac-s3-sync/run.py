import configparser
import os
from subprocess import (
    run,
    check_output,
    CalledProcessError,
    STDOUT, DEVNULL
)

def sync(config, source_bucket_name, dest_bucket_name, env):
    source_bucket_name = config.get('minio', 'source_bucket')
    dest_bucket_name = config.get('minio', 'destination_bucket')
    run(["aws", "s3", 
         "sync", 
         f"s3://{source_bucket_name}",
        f"s3://{dest_bucket_name}"], 
        env=env)
    
def sync_daily(config, env):
    new_env = add_env_vars(env,
                           {"AWS_ACCESS_KEY_ID": "longtest",
                            "AWS_SECRET_ACCESS_KEY": "longtest",
                            "AWS_DEFAULT_REGION": "us-east-1",
                            "AWS_REGION": "us-east-1",
                            "AWS_ENDPOINT_URL": "http://localhost:9001"
                            })

    source_bucket_name = config.get('minio', 'source_bucket')
    dest_bucket_name = config.get('minio', 'destination_bucket')
    sync(source_bucket_name, dest_bucket_name, new_env)

    s3 = make_s3_resource(config)
    source_bucket = s3.Bucket(source_bucket_name)
    dest_bucket = s3.Bucket(dest_bucket_name)

    # Build a set of the source and destination
    # Populate them
    for pfix in get_prefixes(config):
        source_set = set()
        dest_set = set()
        for bucket, s in zip([source_bucket, dest_bucket], [source_set, dest_set]):
            for obj in bucket.objects.filter(Prefix=f"{pfix}/"):
                head = s3.Object(source_bucket_name,obj.key)
                s.add((obj.key, head.content_length))
        if source_set == dest_set:
            print(f"OK {len(source_set)} OBJECTS")
        else:
            print("KO")


# docker run --network host -e ENV=LOCAL -v "$PWD":/python jadudm/s3sync
if __name__ in "__main__":

    config = configparser.ConfigParser()
    config.read(r'config.txt')
    env = extend_path(['/sync', '/sync/minio-binaries'])

    create_minio_alias(config, env)
    create_buckets(config, env,
                   ["gsa-fac-private-s3",
                    "fac-census-to-gsafac-s3",
                    "daily-sync-gsa-fac-private-s3",
                    "weekly-sync-gsa-fac-private-s3"
                    ])
    sync_daily(config, env)
