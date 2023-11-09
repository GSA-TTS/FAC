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

create or replace function getter(base text, item text) returns text 
as $getter$
begin 
	return current_setting(concat(base, '.', item), true);
end;
$getter$ language plpgsql;

create or replace function get_jwt_claim(item text) returns text 
as $get_jwt_claim$
begin 
	return getter('request.jwt.claim', item);
end;
$get_jwt_claim$ language plpgsql;

create or replace function get_header(item text) returns text
as $get_header$
begin 
	raise info 'request.header % %', item, getter('request.header', item);
	return getter('request.header', item);
end;
$get_header$ LANGUAGE plpgsql;

-- https://api-umbrella.readthedocs.io/en/latest/admin/api-backends/http-headers.html
-- I'd like to go to a model where we provide the API keys. 
-- However, for now, we're going to look for a role attached to an api.data.gov account.
-- These come in on `X-Api-Roles` as a comma-separated string.
create or replace function has_tribal_data_access() returns boolean
as $has_tribal_data_access$
declare 
    roles text;
begin 
	select get_header('x-api-roles') into roles;
    return (roles like '%fac_gov_tribal_access%');
end;
$has_tribal_data_access$ LANGUAGE plpgsql;

create or replace function has_public_data_access_only() returns boolean
as $has_public_data_access_only$
begin 
    return not has_tribal_data_access();
end;
$has_public_data_access_only$ LANGUAGE plpgsql;


NOTIFY pgrst, 'reload schema';