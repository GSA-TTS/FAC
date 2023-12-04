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

create or replace function admin_api_v1_0_0.getter(base text, item text) returns text 
as $getter$
begin 
	return current_setting(concat(base, '.', item), true);
end;
$getter$ language plpgsql;

create or replace function admin_api_v1_0_0.get_jwt_claim(item text) returns text 
as $get_jwt_claim$
begin 
	return admin_api_v1_0_0.getter('request.jwt.claim', item);
end;
$get_jwt_claim$ language plpgsql;

create or replace function admin_api_v1_0_0.get_header(item text) returns text
as $get_header$
begin 
	return admin_api_v1_0_0.getter('request.header', item);
end;
$get_header$ LANGUAGE plpgsql;

create or replace function admin_api_v1_0_0.get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select admin_api_v1_0_0.get_header('X-Api-User-Id') into uuid;
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
begin
    SELECT admin_api_v1_0_0.get_api_key_uuid() INTO uuid_header;

    insert into public.support_adminapievent 
        (api_key_uuid, event, event_data, "timestamp")
        values (uuid_header, event, meta, NOW());

    RAISE INFO 'ADMIN_API % % %', uuid_header, event, meta; 
    return 1;
end;
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
            SELECT permissions
            FROM public.support_administrative_key_uuids aku 
            WHERE aku.permissions like '%' || perm || '%')
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO has_permission;

    SELECT 
        CASE WHEN EXISTS (
            SELECT uuid 
            FROM public.support_administrative_key_uuids aku
            WHERE aku.uuid = uuid_header)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    
    -- RAISE INFO 'ADMIN_API has_access_check % % %', uuid_header, key_exists, has_permission;
    PERFORM admin_api_v1_0_0.log_admin_api_event('access_check', 
                                                 json_build_object('uuid', uuid_header, 
                                                                   'key_exists', key_exists,
                                                                   'has_permission', has_permission));
    RETURN key_exists AND has_permission;
END;
$has_admin_data_access$ LANGUAGE plpgsql;

-- Takes an email address and, if that address is not in the access table,
-- inserts it. If the address already exists, the insert is skipped.
-- ### Example
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
DECLARE already_exists INTEGER;
BEGIN
    -- Are they already in the table?
    SELECT count(up.email) 
        FROM public.users_userpermission as up
        WHERE email = params->>'email' INTO already_exists;

    -- If the API user has insert permissions, and the email passed in 
    -- is not already in the table, then insert them.
    IF (admin_api_v1_0_0.has_admin_data_access('INSERT')
       AND (already_exists = 0))
    THEN
        INSERT INTO public.users_userpermission
            (email, permission_id, user_id)
            VALUES (params->>'email', 1, null);
        RETURN admin_api_v1_0_0.log_admin_api_event('tribal-access-email-added', 
                                                    json_build_object('email', params->>'email'));
        PERFORM admin_api_v1_0_0.log_admin_api_event('add_tribal_access', params);
    ELSE
        RETURN 0;
    END IF;
end;
$add_tribal_access_email$ LANGUAGE plpgsql;


-- Adds many email addresses. Calls `add_tribal_access_email` for each address.
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
        FOR em IN (SELECT json_array_elements_text((params->>'emails')::JSON) ele)
        LOOP
            PERFORM admin_api_v1_0_0.add_tribal_access_email(json_build_object('email', em.ele)::JSON);
        END LOOP;
        RETURN 1;
    END IF;
    RETURN 0;
END;
$add_tribal_access_emails$ LANGUAGE plpgsql;

-- Removes the email. Will remove multiple rows. That shouldn't happen, but still.
-- ### Example
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
        -- RAISE INFO 'ADMIN API REMOVE ACCESS %', params->>'email';
        DELETE FROM public.users_userpermission as up
            WHERE up.email = params->>'email';
        GET DIAGNOSTICS affected_rows = ROW_COUNT;
        IF affected_rows <> 0
        THEN
            RETURN admin_api_v1_0_0.log_admin_api_event('tribal-access-email-removed', 
                                                        json_build_object('email', params->>'email'));
        ELSE
            RETURN 0;
        END IF;
    ELSE
        RETURN 0;
    END IF;
end;
$add_tribal_access_email$ LANGUAGE plpgsql;

-- Removes many email addresses. Calls `remove_tribal_access_email` for each address.
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
