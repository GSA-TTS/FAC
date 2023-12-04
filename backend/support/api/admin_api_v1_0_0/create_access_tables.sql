-- This is explicitly not a Django managed table.
-- In order to have an administrative key added,
-- it must be added via a Github commit, and a PR 
-- must be performed to merge the key into the tree.

-- This is because administrative keys can read/write
-- to some tables in the database. They can read internal and
-- in-flight data.
DROP TABLE IF EXISTS administrative_key_uuids;

CREATE TABLE administrative_key_uuids 
    (
        id BIGSERIAL PRIMARY KEY,
        email TEXT,
        uuid TEXT,
        permissions TEXT,
        added DATE
    );

INSERT INTO administrative_key_uuids 
    (email, uuid, permissions, added)
    VALUES
    (
        'matthew.jadud@gsa.gov',
        '61ba59b2-f545-4c2f-9b24-9655c706a06c',
        'SELECT,INSERT,DELETE',
        '2023-12-04'
    ),
    (
        'carley.jackson@gsa.gov',
        'a938cfca-c8eb-4065-b2eb-782d04bd58ef',
        'SELECT,INSERT,DELETE',
        '2023-12-04'
    );
