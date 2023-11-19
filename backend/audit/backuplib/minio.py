from subprocess import (
    run,
    STDOUT, DEVNULL
)

def create_minio_alias(config, env):
    endpoint = config.get('minio', 'endpoint')
    minio_user = config.get('minio', 'user')
    minio_pass = config.get('minio', 'pass')
    run(["mc",
         "alias", "set", "myminio",
         endpoint,
         minio_user,
         minio_pass,
         ],
        env=env,
        stderr=DEVNULL, stdout=DEVNULL)

