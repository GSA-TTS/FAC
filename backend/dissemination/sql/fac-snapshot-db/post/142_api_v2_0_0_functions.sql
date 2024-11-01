-----------------------------------------------------
-- get_header
-- Reaches into the headers provided through PostgREST in order to
-- grab a particular value, keyed by the header key (e.g. "x-api-key") 
-----------------------------------------------------
CREATE OR REPLACE FUNCTION api_v2_0_0_functions.get_header(item text) RETURNS TEXT
    AS $get_header$
    DECLARE res TEXT;
   	BEGIN
    	SELECT (current_setting('request.headers', true)::json)->>item INTO res;
    	RETURN res;
   END;
$get_header$ LANGUAGE plpgsql;

-----------------------------------------------------
-- get_api_key_uuid
-- Uses the get_header function to grab the user id provided by api.data.gov
-----------------------------------------------------
CREATE OR REPLACE FUNCTION api_v2_0_0_functions.get_api_key_uuid() RETURNS TEXT
AS $gaku$
DECLARE uuid TEXT;
BEGIN
	SELECT api_v2_0_0_functions.get_header('x-api-user-id') INTO uuid;
	RETURN uuid;
end;
$gaku$ LANGUAGE plpgsql;

-----------------------------------------------------
-- has_tribal_data_access
-- Determines whether the key id in question has been granted 
-- tribal data access. Required for accessing all of the suppressed tables.
-----------------------------------------------------
CREATE OR REPLACE FUNCTION api_v2_0_0_functions.has_tribal_data_access() 
RETURNS BOOLEAN
AS $has_tribal_data_access$
DECLARE 
    uuid_header UUID;
    key_exists BOOLEAN;
BEGIN
    SELECT api_v2_0_0_functions.get_api_key_uuid() INTO uuid_header;
    SELECT 
        CASE WHEN EXISTS (
            SELECT key_id 
            FROM dissem_copy.dissemination_tribalapiaccesskeyids taaki
            WHERE taaki.key_id = uuid_header::TEXT)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    -- RAISE INFO 'api_v2_0_0 has_tribal % %', uuid_header, key_exists;
    RETURN key_exists;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;
