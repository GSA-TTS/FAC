# loading public data

This script loads public data.

## Grab the ZIP

You'll need to grab

https://drive.google.com/drive/folders/1gUsqD31Pkd17CruE4PWwwPKJVUssYNnI

which is cleaned/historic public data, fit for our dissem_* tables.

Compressed, it is 330MB. Uncompressed, around 3GB.

Put it in dissemination/tools/load_public_dissem_data (this directory)

## Run the script

```
./load_public_data_locally.sh
```

Note you need to run it from within that directory.

## Or, run the Dockerfile

If you're on a Mac, you may want to run the docker container to do the load.

First, build the container.

```
docker build -t facloaddata .
```

Then, with the zipfile of data in the current directory:

```
docker run -i --rm -v ${PWD}:/app \
    --network container:backend-web-1 \
    -t facloaddata
```

The `--network` flag tells Docker to run this container on the same network as your currently running stack. It assumes that you did a `docker compose up` on the FAC stack, and that the web container has the default name of `backend-web-1`. If this does not work, you will need to do a 

```
docker ps
```

and discover the name of a container running in your FAC stack. Once you do this, it will be possible for the loader script to find the Postgres databases.

