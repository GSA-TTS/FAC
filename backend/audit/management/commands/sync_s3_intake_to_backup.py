import configparser
import logging
from subprocess import run
from audit.backuplib.env import (
    add_env_vars,
    extend_path
    )
from audit.backuplib.s3 import (
    create_s3_buckets,
    get_s3_prefixes_from_config,
    make_s3_resource
    )
from audit.backuplib.minio import (
    create_minio_alias
)

from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)

def sync(source_bucket_name, dest_bucket_name, env):
    run(["aws", "s3", 
         "sync", 
         f"s3://{source_bucket_name}",
        f"s3://{dest_bucket_name}"], 
        env=env)

# FIXME: Many things want for a better underlying config structure.
# With a better config, I could grab these things from the app config,
# and it would not matter if I was running locally or in the cloud.
# Put another way: I want to write code and not care where I am running for
# things like this.
def sync_daily(config, env):
    source_bucket_name = config.get('minio', 'source_bucket')
    dest_bucket_name = config.get('minio', 'destination_bucket')
    sync(source_bucket_name, dest_bucket_name, env)

    s3 = make_s3_resource(config)
    source_bucket = s3.Bucket(source_bucket_name)
    dest_bucket = s3.Bucket(dest_bucket_name)

    # Build a set of the source and destination
    # Populate them
    for pfix in get_s3_prefixes_from_config(config):
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
class Command(BaseCommand):

    def handle(self, *args, **options):
        config = configparser.ConfigParser()
        config.read(r'audit/backuplib/config.txt')
        env = extend_path(['/sync', '/sync/minio-binaries'])
        new_env = add_env_vars(env,
                            {"AWS_ACCESS_KEY_ID": "longtest",
                                "AWS_SECRET_ACCESS_KEY": "longtest",
                                "AWS_DEFAULT_REGION": "us-east-1",
                                "AWS_REGION": "us-east-1",
                                "AWS_ENDPOINT_URL": config.get('minio', 'endpoint')
                                })
        
        create_minio_alias(config, new_env)
        create_s3_buckets(config, new_env,
                    ["gsa-fac-private-s3",
                        "fac-census-to-gsafac-s3",
                        "daily-sync-gsa-fac-private-s3",
                        "weekly-sync-gsa-fac-private-s3"
                        ])
        
        sync_daily(config, new_env)
