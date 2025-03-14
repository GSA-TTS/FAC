# loading public data

This provides a containerized data loading process that sets up your local FAC in a manner that duplicates the live/production app.

The data we are using is public, historic data. It can be replaced, at a later point, with data that is more current.

## Full clean

You might want a completely clean local stack to start. It is not strictly necessary. If you get key conflicts, it means you already have some of this historic data loaded.

### Wipe the stack

From the backend folder

```
make -i docker-full-clean
```

Note the `-i` flag. This means `make` should ignore errors. You want it to, so it will keep going and wipe everything.

```
make docker-first-run
```

and then

```
docker compose up
```

We need the stack running for this whole process.

## Grab the ZIP

You'll need to grab `db_dissem_dump.zip`:

https://drive.google.com/drive/folders/1gUsqD31Pkd17CruE4PWwwPKJVUssYNnI

which is cleaned/historic public data, fit for our dissem_* tables.

Compressed, it is 330MB. Uncompressed, around 3GB.

Put it in util/load_public_dissem_data/data (a child of this directory)

## Build the container

This is containerized, so it should work on all platforms. To build the container, run

```
make build
```

Then, to run the container,

```
make run
```

You need to run this from the current directory.

NOTE: Windows machines will need to use \$\{CURDIR\} rather than \$\{PWD\} for `make run`, as PWD is not recognizable.

NOTE: The docker command in the Makefile uses the `--network` flag. The `--network` flag tells Docker to run this container on the same network as your currently running stack. It assumes that you did a `docker compose up` on the FAC stack, and that the web container has the default name of `backend-web-1`. If this does not work, you will need to...

```
make NETWORK=<container-name> run
```

where `<container-name>` is the name of your web container. This should allow this container to correctly talk to our databases.

## When to rebuild this container

Note this is pinned to v0.1.9 of the cgov-util.

https://github.com/GSA-TTS/fac-backup-utility

If that gets updated, you'll need to update the dockerfile.

It also copies in the YAML for sling from `dissemination/sql/sling`. If that changes, you'll want to
