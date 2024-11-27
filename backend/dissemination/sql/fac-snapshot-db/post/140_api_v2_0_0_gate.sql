------------------------------------------------------------------
-- GATE
------------------------------------------------------------------
-- We only want the API to run if certain conditions are met.
-- We could try and encode that in the `bash` portion of the code.
-- Or, we could just gate things at the top of our SQL. 
-- If the conditions are not met, we should exit noisily.
-- A cast to regclass will fail with an exception if the table
-- does not exist.
DO LANGUAGE plpgsql
$GATE$
    DECLARE
        the_schema varchar := 'public_data_v1_0_0';
        the_table  varchar := 'metadata';
        api_ver    varchar := 'api_v2_0_0';
    BEGIN
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE  schemaname = the_schema
            AND    tablename  = the_table
            )
        THEN
            RAISE info '% Gate condition met. Continuing.', api_ver;
        ELSE
            RAISE exception '% %.% not found.', api_ver, the_schema, the_table;
        END IF;
    END
$GATE$;
