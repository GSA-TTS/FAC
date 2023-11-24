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

create or replace function api_v1_0_3.getter(base text, item text) returns text 
as $getter$
begin 
	return current_setting(concat(base, '.', item), true);
end;
$getter$ language plpgsql;

create or replace function api_v1_0_3.get_jwt_claim(item text) returns text 
as $get_jwt_claim$
begin 
	return api_v1_0_3.getter('request.jwt.claim', item);
end;
$get_jwt_claim$ language plpgsql;

create or replace function api_v1_0_3.get_header(item text) returns text
as $get_header$
begin 
	-- raise info 'request.header % %', item, getter('request.header', item);
	return api_v1_0_3.getter('request.header', item);
end;
$get_header$ LANGUAGE plpgsql;

-- https://api-umbrella.readthedocs.io/en/latest/admin/api-backends/http-headers.html
-- Previously, we were using a role attached to the key.
-- This now uses an explicit table to determine if a key has tribal data access.
-- What this means is that we must go through a commit/PR process in order to use
-- keys that will have access to tribal data. This should be supported by a 
-- ticketing process.
create or replace function api_v1_0_3.has_tribal_data_access() returns boolean
as $has_tribal_data_access$
DECLARE 
    uuid_header text;
    key_exists boolean;
BEGIN
    SELECT api_v1_0_3.get_header('x-api-user-id') into uuid_header;
    SELECT 
        CASE WHEN EXISTS (
            SELECT uuid 
            FROM tribal_access_api_key_uuids tak
            WHERE tak.uuid = uuid_header)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    
    RETURN key_exists;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;

create or replace function api_v1_0_3.has_public_data_access_only() returns boolean
as $has_public_data_access_only$
begin 
    return not api_v1_0_3.has_tribal_data_access();
end;
$has_public_data_access_only$ LANGUAGE plpgsql;


NOTIFY pgrst, 'reload schema';
