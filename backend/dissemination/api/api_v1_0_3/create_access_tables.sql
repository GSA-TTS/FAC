-- This is explicitly not a Django managed table.
-- In order to grant an API key access to read tribal data
-- we need to go through a PR.

DROP TABLE IF EXISTS tribal_access_api_key_uuids;

CREATE TABLE tribal_access_api_key_uuids
    (
        id BIGSERIAL PRIMARY KEY,
        email TEXT,
        uuid TEXT,
        added DATE
    );

INSERT INTO tribal_access_api_key_uuids 
    (email, uuid, added)
    VALUES
    (
        'matthew.jadud@gsa.gov',
        '18ef0e72-8976-11ee-ad35-3f80b454d3cc',
        '2023-11-22'
    );
