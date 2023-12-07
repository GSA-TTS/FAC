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

begin;


CREATE OR REPLACE FUNCTION admin_api_v1_0_0.get_header(item text) RETURNS text
    AS $get_header$
    declare res text;
   	begin
    	SELECT (current_setting('request.headers', true)::json)->>item into res;
    	return res;
   end;
$get_header$ LANGUAGE plpgsql;

create or replace function admin_api_v1_0_0.get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select admin_api_v1_0_0.get_header('x-api-user-id') into uuid;
	return uuid;
end;
$gaku$ LANGUAGE plpgsql;

-- log_api_event
-- Maintain an internal table of administrative API events.
-- Also RAISE INFO so that NR gets a copy.
create or replace function admin_api_v1_0_0.log_admin_api_event(event TEXT, meta JSON)
returns boolean
as $log_admin_api_event$
DECLARE
    uuid_header text;
BEGIN
    SELECT admin_api_v1_0_0.get_api_key_uuid() INTO uuid_header;

    INSERT INTO public.support_adminapievent 
        (api_key_uuid, event, event_data, "timestamp")
        VALUES (uuid_header, event, meta, NOW());

    RAISE INFO 'ADMIN_API % % %', uuid_header, event, meta; 
    RETURN 1;
END;
$log_admin_api_event$ LANGUAGE plpgsql;


-- has_admin_data_access :: permission -> bool
-- The permissions (insert, select, delete) allow us to have users who can 
-- read administrative data in addition to users who can (say) update 
-- select tables like the tribal access lists.
create or replace function admin_api_v1_0_0.has_admin_data_access(perm TEXT) returns boolean
as $has_admin_data_access$
DECLARE 
    uuid_header text;
    key_exists boolean;
    has_permission boolean;
BEGIN
    SELECT admin_api_v1_0_0.get_api_key_uuid() INTO uuid_header;

    SELECT 
        CASE WHEN EXISTS (
            SELECT uuid 
            FROM public.support_administrative_key_uuids aku
            WHERE aku.uuid = uuid_header)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;

    SELECT 
        CASE WHEN EXISTS (
            SELECT permissions
            FROM public.support_administrative_key_uuids aku 
            WHERE aku.uuid = uuid_header
            AND aku.permissions like '%' || perm || '%')
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO has_permission;
    
    -- This log event is an INSERT. When called from a VIEW (a SELECT-only context),
    -- a call to log_admin_api_event() fails. So, we'll RAISE INFO right here, so we can
    -- see the resultse of access checks in the log. We might later comment this out if 
    -- it becomes too noisy.
    RAISE INFO 'ADMIN_API has_access_check % % %', uuid_header, key_exists, has_permission;

    RETURN key_exists AND has_permission;
END;
$has_admin_data_access$ LANGUAGE plpgsql;

-- Takes an email address and, if that address is not in the access table,
-- inserts it. If the address already exists, the insert is skipped.
-- 
-- ### Example from REST client
-- POST http://localhost:3000/rpc/add_tribal_access_email
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_0_0
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "email": "darth.vader@deathstar.org"
-- }
create or replace function admin_api_v1_0_0.add_tribal_access_email(params JSON) 
returns BOOLEAN
as $add_tribal_access_email$
DECLARE 
    already_exists INTEGER;
    read_tribal_id INTEGER;
BEGIN
    -- If the API user has insert permissions, give it a go
    IF admin_api_v1_0_0.has_admin_data_access('INSERT')
    THEN
        -- Are they already in the table?
        SELECT count(up.email) 
            FROM public.users_userpermission as up
            WHERE email = params->>'email' INTO already_exists;

        -- If they are, we're going to exit.
        IF already_exists <> 0
        THEN
            RETURN 0;
        END IF;

        -- Grab the permission ID that we need for the insert below.
        -- We want the 'read-tribal' permission, which has a human-readable
        -- slug. But, we need it's ID, because that is the PK.
        SELECT up.id INTO read_tribal_id 
            FROM public.users_permission AS up
            WHERE up.slug = 'read-tribal';

        IF already_exists = 0 
        THEN
            -- Can we make the 1 not magic... do a select into.
            INSERT INTO public.users_userpermission
                (email, permission_id, user_id)
                VALUES (params->>'email', read_tribal_id, null);
            RETURN admin_api_v1_0_0.log_admin_api_event('tribal-access-email-added', 
                                                        json_build_object('email', params->>'email'));
        END IF;
    ELSE
        RETURN 0;
    END IF;
end;

-- Adds many email addresses. Calls `add_tribal_access_email` for each address.
--
-- ### Example from REST client
-- POST http://localhost:3000/rpc/add_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_0_0
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "emails": [
--         "darth.vader@deathstar.org",
--         "bob.darth.vader@deathstar.org",
--         "darthy.vader@deathstar.org",
--         "bob@deathstar.org"
--     ]
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_0_0.add_tribal_access_emails(params JSON) 
returns BOOLEAN
as $add_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_0_0.has_admin_data_access('INSERT')
    THEN 
        -- This is a FOR loop over a JSON array in plPgSQL
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            -- PERFORM is how to execute code that does not return anything.
            -- If a SELECT was used here, the SQL compiler would complain.
            PERFORM admin_api_v1_0_0.add_tribal_access_email(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$add_tribal_access_emails$ LANGUAGE plpgsql;

-- Removes the email. Will remove multiple rows. That shouldn't happen, but still.
--
-- ### Example from REST client
-- POST http://localhost:3000/rpc/remove_tribal_access_email
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_0_0
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "email": "darth.vader@deathstar.org"
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_0_0.remove_tribal_access_email(params JSON) 
returns BOOLEAN
as $add_tribal_access_email$
DECLARE
      affected_rows INTEGER;
BEGIN

    IF admin_api_v1_0_0.has_admin_data_access('DELETE')
    THEN 
        -- Delete rows where the email address matches
        DELETE FROM public.users_userpermission as up
            WHERE up.email = params->>'email';
        -- This is the Postgres way to find out how many rows
        -- were affected by a DELETE.
        GET DIAGNOSTICS affected_rows = ROW_COUNT;
        -- If that is greater than zero, we were successful.
        IF affected_rows > 0
        THEN
            RETURN admin_api_v1_0_0.log_admin_api_event('tribal-access-email-removed', 
                                                        json_build_object('email', params->>'email'));
        ELSE
            RETURN 0;
        END IF;
    ELSE
        -- If we did not have permission, consider it a failure.
        RETURN 0;
    END IF;
end;
$add_tribal_access_email$ LANGUAGE plpgsql;

-- Removes many email addresses. Calls `remove_tribal_access_email` for each address.
-- 
-- ### Example from REST client
-- POST http://localhost:3000/rpc/remove_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_0_0
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "emails": [
--         "darth.vader@deathstar.org",
--         "bob.darth.vader@deathstar.org",
--         "darthy.vader@deathstar.org",
--         "bob@deathstar.org"
--     ]
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_0_0.remove_tribal_access_emails(params JSON) 
returns BOOLEAN
as $remove_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_0_0.has_admin_data_access('DELETE')
    THEN 
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            PERFORM admin_api_v1_0_0.remove_tribal_access_email(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$remove_tribal_access_emails$ LANGUAGE plpgsql;

commit;

NOTIFY pgrst, 'reload schema';
