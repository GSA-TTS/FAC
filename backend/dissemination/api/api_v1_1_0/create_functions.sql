-- WARNING
-- Under PostgreSQL 12, the functions below work.
-- Under PostgreSQL 14, these will break.
--
-- Note the differences:
--
-- raise info 'Works under PostgreSQL 12';
-- raise info 'request.header.x-magic %', (SELECT current_setting('request.header.x-magic', true));
-- raise info 'request.jwt.claim.expires %', (SELECT current_setting('request.jwt.claim.expires', true));
-- raise info 'Works under PostgreSQL 14';
-- raise info 'request.headers::json->>x-magic %', (SELECT current_setting('request.headers', true)::json->>'x-magic');
-- raise info 'request.jwt.claims::json->expires %', (SELECT current_setting('request.jwt.claims', true)::json->>'expires');
--
-- To quote the work of Dav Pilkey, "remember this now."

-- We don't grant tribal access (yet)
create or replace function api_v1_1_0_functions.has_tribal_data_access() 
returns boolean
as $has_tribal_data_access$
DECLARE 
    uuid_header UUID;
    key_exists boolean;
BEGIN

    SELECT admin_api_v1_1_0_functions.get_api_key_uuid() INTO uuid_header;
    SELECT 
        CASE WHEN EXISTS (
            SELECT key_id 
            FROM public.dissemination_TribalApiAccessKeyIds taaki
            WHERE taaki.key_id = uuid_header::TEXT)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    RETURN key_exists;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;


NOTIFY pgrst, 'reload schema';
