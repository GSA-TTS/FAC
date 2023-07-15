# Deploying a new API

An API in PostgREST needs a few things to happen. 

1. A JWT secret needs to be loaded into the PostgREST environment.
2. We need to tear down what was
3. We need to stand it back up again

# Creating a JWT secret

The command

```
fac create_api_jwt <role> <passphrase>
```

creates a JWT secret. The passphrase must be [at least 32 characters long](https://postgrest.org/en/v10.2/tutorials/tut1.html#:~:text=32%20characters%20long.-,Note,-Unix%20tools%20can).

For example:

```
fac create_api_jwt api_fac_gov mooE1Olp7u3xwgeDihtrjX14vbX9fH27
```

This will create the JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBpX2ZhY19nb3ZfYW5vbiIsImNyZWF0ZWQiOiIyMDIzLTA3LTE0VDIxOjA0OjA2LjEyMDU0OCIsImV4cGlyZXMiOiIyMDI0LTAxLTE0VDIxOjA0OjA2LjEyMDUyMCIsImV4cCI6MTcwNTI2NjI0Nn0.cu2EVrP5X5u6uxVffeHLDNI24pfYyyICKD3wm1UtWts
```

This has three pieces:

```
header.payload.signature
```

**The data can be decoded without the passphrase.** So, a JWT token is not a way of *encrypting* data. Do not put any privileged information in a JWT.

However, without the passphrase, the signature cannot be verified. PostgREST will not accept a JWT as valid that does not have a good signature. Therefore, it should be the case that only JWTs we create, with this tool, signed with a passphrase we know, can be accepted by our stack as valid.

We pass `role` and `exp`, which are fields that PostgREST expect. We add two human-readable fields, `created` and `expires`. All tokens generated with this tool expire after 6 months, and must be refreshed at api.data.gov. If we don't refresh the token, api.data.gov (meaning api.fac.gov) will stop working.

FIXME: We do not yet have logic in the code that will reject the JWT after it expires. This should be added.

## Using the JWT token

For symmetric use, that passphrase must be loaded into a GH Secret, and that secret deployed to our environments via Terraform. In this way, our PostgREST container knows how to verify the integrity of JWTs that are sent to us.

Our JWT only lives at api.data.gov. We will put it in the `Authorization: Bearer <jwt>` header. In this way, only API requests that come through api.data.gov (meaning requests that go to api.fac.gov) will be executed by PostgREST. All other queries, from all other sources, will be rejected.

It is important that the role you choose matches the role we expect for public queries. Our schemas are attached to the role `api_fac_gov`. 

### Limiting access

We use the `X-Api-Roles` header from api.data.gov to determine some levels of access.

https://api-umbrella.readthedocs.io/en/latest/admin/api-backends/http-headers.html

the stored procedure

```
has_tribal_data_access()
```

checks this header, and if the correct role is present (`fac_gov_tribal_data_access`), we will accept the query as being privileged. The role has to be attached to the key by an administrator.

## Standing up / tearing down

With each deployment of the stack, we should tear down and stand up the entire API. 

1. `fac drop_deprecated_schema_and_views` will tear down any deprecated APIs. Always run it.
1. `fac drop_api_schema` will tear down the active schema and everything associated with it.
2. `fac create_api_schema` will create roles and the schema.
3. `fac create_api_views` will create the views on the data.

With this sequence, we completely tear down old *and* current APIs, as well as associated roles. Then, we stand them up again, including all roles. This guarantees that every deploy is a complete, fresh instantiation of the API, and any changes that may have been made to views, functions, or privileges are caught.

In other words: the API should always be stood up from a "blank slate" in the name of stateless deploys.

# API versions

When adding a new API version.

1. Create a folder in api/dissemination for the version name. E.g. `v1_0_1`. 
2. Copy the contents of an existing API as a starting point.
3. Update `docker-compose.yml` and `docker-compose-web.yml` to change the `PGRST_DB_SCHEMAS` key to reflect all the active schemas. 
   1. ADD TO THE END OF THIS LIST. The first entry is the default. Only add to the front of the list if we are certain the schema should become the new default.
   2. This is likely true of TESTED patch version bumps (v1_0_0 to v1_0_1), and *maybe* minor version bumps (v1_0_0 to v1_1_0). MAJOR bumps require change management messaging.
4. Update `APIViewTests` to make sure you're testing the right schema. (That file might want some love...)
