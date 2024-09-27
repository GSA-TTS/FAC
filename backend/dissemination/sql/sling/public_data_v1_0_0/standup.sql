-- WE DO NEED THE TABLES, THOUGH.
-- In theory, `sling` will be creating these tables. But, if they don't exist,
-- then the views will crash. So, lets go ahead and create the tables if they don't exist.
-- This means we have to stay in sync with the sling YAML.

CREATE TABLE IF NOT EXISTS public_data_v1_0_0
