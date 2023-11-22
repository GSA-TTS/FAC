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

create or replace function get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select get_header('X-Api-User-Id') into uuid;
    return uuid;
end;
$gaku$ LANGUAGE plpgsql;

create or replace function has_admin_data_access() returns boolean
as $has_admin_data_access$
declare 
    roles text;
begin 
	select get_header('x-api-roles') into roles;
    return (roles like '%fac_gov_admin_access%');
end;
$has_admin_data_access$ LANGUAGE plpgsql;


-- log_api_event
create or replace function log_admin_api_event(event TEXT, meta JSON)
returns boolean
as $log_admin_api_event$
begin
    insert into public.support_adminapievent values (
        get_api_key_uuid(),
        event, 
        meta
        ); 
    return 1;
end;
$log_admin_api_event$ LANGUAGE plpgsql;



create or replace function add_tribal_access_email(email TEXT) 
returns BOOLEAN
as $add_tribal_access_email$
begin; 
    RETURN 1;
end;
$add_tribal_access_email$ LANGUAGE plpgsql;


commit;

NOTIFY pgrst, 'reload schema';
