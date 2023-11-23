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
	-- raise info 'request.header % %', item, getter('request.header', item);
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

create or replace function admin_api_v1_0_0.has_admin_data_access(perm TEXT) returns boolean
as $has_admin_data_access$
DECLARE 
    -- roles_header text;
    uuid_header text;
    key_exists boolean;
    has_permission boolean;
BEGIN
	-- SELECT admin_api_v1_0_0.get_header('x-api-roles') into roles_header;
    SELECT admin_api_v1_0_0.get_header('x-api-user-id') into uuid_header;

    SELECT 
        CASE WHEN EXISTS (
            SELECT permissions
            FROM administrative_key_uuids aku 
            WHERE aku.permissions like '%' || perm || '%')
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO has_permission;

    SELECT 
        CASE WHEN EXISTS (
            SELECT uuid 
            FROM administrative_key_uuids aku
            WHERE aku.uuid = uuid_header)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    
    RAISE INFO 'ADMIN_API_ACCESS % % %', uuid_header, key_exists, has_permission;
    RETURN key_exists AND has_permission;
END;
$has_admin_data_access$ LANGUAGE plpgsql;


-- log_api_event
create or replace function admin_api_v1_0_0.log_admin_api_event(event TEXT, meta JSON)
returns boolean
as $log_admin_api_event$
begin
    insert into public.support_adminapievent 
        (api_key_uuid, event, event_data, "timestamp")
        values (get_api_key_uuid(), event, meta, NOW()); 
    return 1;
end;
$log_admin_api_event$ LANGUAGE plpgsql;

create or replace function admin_api_v1_0_0.add_tribal_access_email(params JSON) 
returns BOOLEAN
as $add_tribal_access_email$
DECLARE already_exists INTEGER;
BEGIN
    SELECT count(up.email) 
        FROM public.users_userpermission as up
        WHERE email = params->>'email' INTO already_exists;

    IF (admin_api_v1_0_0.has_admin_data_access('INSERT')
       AND (already_exists = 0))
    THEN 
        INSERT INTO public.users_userpermission
            (email, permission_id, user_id)
            VALUES (params->>'email', 1, null);
        RETURN admin_api_v1_0_0.log_admin_api_event('tribal-access-email-added', 
                                                    json_build_object('email', params->>'email'));
    ELSE
        RETURN 0;
    END IF;
end;
$add_tribal_access_email$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION admin_api_v1_0_0.remove_tribal_access_email(params JSON) 
returns BOOLEAN
as $add_tribal_access_email$
DECLARE
      affected_rows INTEGER;
BEGIN

    IF admin_api_v1_0_0.has_admin_data_access('DELETE')
    THEN 
        RAISE INFO 'ADMIN API REMOVE ACCESS %', params->>'email';
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
