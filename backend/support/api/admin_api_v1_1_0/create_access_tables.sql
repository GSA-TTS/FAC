-- This is explicitly not a Django managed table.
-- In order to have an administrative key added,
-- it must be added via a Github commit, and a PR
-- must be performed to merge the key into the tree.

-- This is because administrative keys can read/write
-- to some tables in the database. They can read internal and
-- in-flight data.

DROP TABLE IF EXISTS support_administrative_key_uuids;

CREATE TABLE support_administrative_key_uuids
    (
        id BIGSERIAL PRIMARY KEY,
        email TEXT,
        uuid TEXT,
        permissions TEXT,
        added DATE
    );

INSERT INTO support_administrative_key_uuids
    (email, uuid, permissions, added)
    VALUES
    (
        'matthew.jadud@gsa.gov',
        '61ba59b2-f545-4c2f-9b24-9655c706a06c',
        'CREATE,READ,DELETE',
        '2023-12-04'
    ),
    (
        'daniel.swick@gsa.gov',
        'b6e08808-ecb2-4b6a-b928-46d4205497ff',
        'CREATE,READ,DELETE',
        '2023-12-08'
    ),
    (
        'fac-gov-test-users+api-tester-admin@gsa.gov',
        'dd60c3f9-053d-4d82-a309-c89da53559f4',
        'CREATE,READ,DELETE',
        '2024-07-10'
    )
    ;

