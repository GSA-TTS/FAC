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


CREATE OR REPLACE FUNCTION admin_api_v1_1_0_functions.get_header(item text) RETURNS text
    AS $get_header$
    declare res text;
   	begin
    	SELECT (current_setting('request.headers', true)::json)->>item into res;
    	return res;
   end;
$get_header$ LANGUAGE plpgsql;

create or replace function admin_api_v1_1_0_functions.get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select admin_api_v1_1_0_functions.get_header('x-api-user-id') into uuid;
	return uuid;
end;
$gaku$ LANGUAGE plpgsql;

-- log_api_event
-- Maintain an internal table of administrative API events.
-- Also RAISE INFO so that NR gets a copy.
create or replace function admin_api_v1_1_0_functions.log_admin_api_event(event TEXT, meta JSON)
returns boolean
as $log_admin_api_event$
DECLARE
    uuid_header text;
BEGIN
    SELECT admin_api_v1_1_0_functions.get_api_key_uuid() INTO uuid_header;

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
create or replace function admin_api_v1_1_0_functions.has_admin_data_access(perm TEXT) returns boolean
as $has_admin_data_access$
DECLARE 
    uuid_header text;
    key_exists boolean;
    has_permission boolean;
BEGIN
    SELECT admin_api_v1_1_0_functions.get_api_key_uuid() INTO uuid_header;

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
-- content-profile: admin_api_v1_1_0
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "email": "darth.vader@deathstar.org"
-- }
create or replace function admin_api_v1_1_0.add_tribal_access_email(params JSON) 
returns BOOLEAN
as $add_tribal_access_email$
DECLARE 
    already_exists INTEGER;
    read_tribal_id INTEGER;
BEGIN
    -- If the API user has insert permissions, give it a go
    IF admin_api_v1_1_0_functions.has_admin_data_access('CREATE')
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
            RETURN admin_api_v1_1_0_functions.log_admin_api_event('tribal-access-email-added', 
                                                        json_build_object('email', params->>'email'));
        END IF;
    ELSE
        RETURN 0;
    END IF;
end;
$add_tribal_access_email$ LANGUAGE plpgsql;

-- Adds many email addresses. Calls `add_tribal_access_email` for each address.
--
-- ### Example from REST client
-- POST http://localhost:3000/rpc/add_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_1_0
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
CREATE OR REPLACE FUNCTION admin_api_v1_1_0.add_tribal_access_emails(params JSON) 
returns BOOLEAN
as $add_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_1_0_functions.has_admin_data_access('CREATE')
    THEN 
        -- This is a FOR loop over a JSON array in plPgSQL
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            -- PERFORM is how to execute code that does not return anything.
            -- If a SELECT was used here, the SQL compiler would complain.
            PERFORM admin_api_v1_1_0.add_tribal_access_email(json_build_object('email', em.ele)::JSON);
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
-- content-profile: admin_api_v1_1_0
-- content-type: application/json 
-- Prefer: params=single-object
-- // Not actually a key UUID.
-- X-Api-User-Id: 18ef0e72-8976-11ee-ad35-3f80b454d3cc
-- {
--     "email": "darth.vader@deathstar.org"
-- }
CREATE OR REPLACE FUNCTION admin_api_v1_1_0.remove_tribal_access_email(params JSON) 
returns BOOLEAN
as $remove_tribal_access_email$
DECLARE
      affected_rows INTEGER;
BEGIN

    IF admin_api_v1_1_0_functions.has_admin_data_access('DELETE')
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
            RETURN admin_api_v1_1_0_functions.log_admin_api_event('tribal-access-email-removed', 
                                                        json_build_object('email', params->>'email'));
        ELSE
            RETURN 0;
        END IF;
    ELSE
        -- If we did not have permission, consider it a failure.
        RETURN 0;
    END IF;
end;
$remove_tribal_access_email$ LANGUAGE plpgsql;

-- Removes many email addresses. Calls `remove_tribal_access_email` for each address.
-- 
-- ### Example from REST client
-- POST http://localhost:3000/rpc/remove_tribal_access_emails
-- authorization: Bearer {{$processEnv CYPRESS_API_GOV_JWT}}
-- content-profile: admin_api_v1_1_0
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
CREATE OR REPLACE FUNCTION admin_api_v1_1_0.remove_tribal_access_emails(params JSON) 
returns BOOLEAN
as $remove_tribal_access_emails$
DECLARE
    ele TEXT;
    em record;
BEGIN
    IF admin_api_v1_1_0_functions.has_admin_data_access('DELETE')
    THEN 
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            PERFORM admin_api_v1_1_0.remove_tribal_access_email(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$remove_tribal_access_emails$ LANGUAGE plpgsql;




--The function below add_tribal_api_key_access adds read access to a tribal API for a specified email.
--It checks if the API user has read permissions.
--If the email already exists in the database, the function returns false.
--Otherwise, it adds the email with 'read-tribal' permission, logs the event, and returns true.

CREATE OR REPLACE FUNCTION admin_api_v1_1_0.add_tribal_api_key_access(params JSON) 
RETURNS BOOLEAN
AS $add_tribal_api_key_access$
DECLARE 
    user_exists BOOLEAN;
BEGIN
    -- If the API user has read permissions, give it a go
    IF admin_api_v1_1_0_functions.has_admin_data_access('CREATE') THEN
    -- Check if the user with the given email
        SELECT EXISTS (
            SELECT 1 
            FROM public.dissemination_TribalApiAccessKeyIds
            WHERE email = params->>'email'
        )
        INTO user_exists;

        -- If the user exists, return false (indicating failure)
        IF user_exists THEN
            RETURN false;
        END IF;

        -- If the user does not exist, add a new record
        INSERT INTO public.dissemination_TribalApiAccessKeyIds (email, key_id, date_added)
        VALUES (params->>'email', params->>'key_id', CURRENT_TIMESTAMP);

    END IF;

    RETURN true; -- Return true to indicate success
END;
$add_tribal_api_key_access$ LANGUAGE plpgsql;

-- The function below removes tribal API key access for a specified email.
-- It checks if the API user has read permissions.
-- If the email exists in the database with 'read-tribal' permission, it removes the entry, logs the removal event, and returns true.
-- If the email doesn't exist or the user lacks proper permissions, the function returns false.

CREATE OR REPLACE FUNCTION admin_api_v1_1_0.remove_tribal_api_key_access(params JSON) 
RETURNS BOOLEAN
AS $remove_tribal_api_key_access$
DECLARE 
    user_exists BOOLEAN;
BEGIN
    -- If the API user has read permissions, give it a go
    IF admin_api_v1_1_0_functions.has_admin_data_access('DELETE') THEN
        -- Check if the user with the given email exists
        SELECT EXISTS (
            SELECT 1 
            FROM public.dissemination_TribalApiAccessKeyIds
            WHERE email = params->>'email'
        )
        INTO user_exists;

        -- If the user exists, remove the record
        IF user_exists THEN
            DELETE FROM public.dissemination_TribalApiAccessKeyIds
            WHERE email = params->>'email';
            RETURN true; -- Return true to indicate success
        ELSE
            RETURN false; -- Return false to indicate failure
        END IF;
    ELSE
        RETURN false; -- Return false if the API user doesn't have read permissions
    END IF;
END;
$remove_tribal_api_key_access$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION admin_api_v1_1_0.request_file_access(
    report_id TEXT
) RETURNS JSON LANGUAGE plpgsql AS
$$
DECLARE
    v_uuid_header TEXT;
    v_access_uuid VARCHAR(200);
    v_key_exists BOOLEAN;
    v_key_added_date DATE;
BEGIN
    
    SELECT admin_api_v1_1_0_functions.get_api_key_uuid() INTO v_uuid_header;

    -- Check if the provided API key exists in public.dissemination_TribalApiAccessKeyIds
    SELECT 
        EXISTS(
            SELECT 1
            FROM public.dissemination_TribalApiAccessKeyIds
            WHERE key_id = v_uuid_header
        ) INTO v_key_exists;
    

    -- Get the added date of the key from public.dissemination_TribalApiAccessKeyIds
    SELECT date_added
    INTO v_key_added_date
    FROM public.dissemination_TribalApiAccessKeyIds
    WHERE key_id = v_uuid_header;
    

    -- Check if the key is less than 6 months old
    IF v_uuid_header IS NOT NULL AND v_key_exists AND v_key_added_date >= CURRENT_DATE - INTERVAL '6 months' THEN
        -- Generate UUID (using PostgreSQL's gen_random_uuid function)
        SELECT gen_random_uuid() INTO v_access_uuid;  
              
        -- Inserting data into the one_time_access table
        INSERT INTO public.dissemination_onetimeaccess (uuid, api_key_id, timestamp, report_id)
        VALUES (v_access_uuid::UUID, v_uuid_header, CURRENT_TIMESTAMP, report_id);

        -- Return the UUID to the user
        RETURN json_build_object('access_uuid', v_access_uuid);
    ELSE
        -- Return an error for unauthorized access
        RETURN json_build_object('error', 'Unauthorized access or key older than 6 months')::JSON;
    END IF;
END;
$$;



commit;

NOTIFY pgrst, 'reload schema';
