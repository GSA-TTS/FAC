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


CREATE OR REPLACE FUNCTION api_v1_1_0_functions.get_header(item text) RETURNS text
    AS $get_header$
    declare res text;
   	begin
    	SELECT (current_setting('request.headers', true)::json)->>item into res;
    	return res;
   end;
$get_header$ LANGUAGE plpgsql;

create or replace function api_v1_1_0_functions.get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select api_v1_1_0_functions.get_header('x-api-user-id') into uuid;
	return uuid;
end;
$gaku$ LANGUAGE plpgsql;

create or replace function api_v1_1_0_functions.has_tribal_data_access() 
returns boolean
as $has_tribal_data_access$
DECLARE 
    uuid_header UUID;
    key_exists boolean;
BEGIN

    SELECT api_v1_1_0_functions.get_api_key_uuid() INTO uuid_header;
    SELECT 
        CASE WHEN EXISTS (
            SELECT key_id 
            FROM public.dissemination_TribalApiAccessKeyIds taaki
            WHERE taaki.key_id = uuid_header::TEXT)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END 
        INTO key_exists;
    RAISE INFO 'api_v1_1_0 has_tribal % %', uuid_header, key_exists;
    RETURN key_exists;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;

-- If you change the constant defined by this function,
-- you must regenerate the index.
CREATE OR REPLACE FUNCTION api_v1_1_0_functions.batch_size()
  RETURNS int
  LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
'SELECT 20000';
GRANT EXECUTE ON FUNCTION api_v1_1_0_functions.batch_size() TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0_functions.batch (id bigint) 
returns bigint 
as $batch$
declare num bigint;
begin
    select div(id, api_v1_1_0_functions.batch_size()) into num;
    return num;
end;
$batch$
language plpgsql immutable;
GRANT EXECUTE ON FUNCTION api_v1_1_0_functions.batch(bigint) TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0.batches (in_table text) 
returns integer 
as $batches$
declare count integer;
declare batch_size bigint;
begin 
    select api_v1_1_0_functions.batch_size() into batch_size;
	case
	   	when in_table = 'general' then  
	   		select div(count(*), batch_size) into count 
	   		from public.dissemination_general;
	   	when in_table = 'federal_awards' then  
	   		select div(count(*), batch_size) into count 
	   		from public.dissemination_federalaward;
	else
		count := 0;
	end case;
	RETURN count;
end;
$batches$   
language plpgsql;
GRANT EXECUTE ON FUNCTION api_v1_1_0.batches(text) TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0.get_general_batch (batch_no bigint) 
returns setof dissemination_general
as $batches$
	select  * from public.dissemination_general where api_v1_1_0_functions.batch(id) = batch_no;
$batches$   
language sql;
GRANT EXECUTE ON FUNCTION api_v1_1_0.get_general_batch(bigint) TO api_fac_gov;

CREATE OR REPLACE FUNCTION api_v1_1_0.get_federal_award_batch (batch_no bigint) 
returns setof dissemination_federalaward
as $batches$
	select  * from public.dissemination_federalaward where api_v1_1_0_functions.batch(public.dissemination_federalaward.id) = batch_no;
$batches$   
language sql;
GRANT EXECUTE ON FUNCTION api_v1_1_0.get_federal_award_batch(bigint) TO api_fac_gov;


-- We should consider dropping and regenerating this index
-- every night after MV generation.
-- drop index batch_by_id_dfa;
create index IF NOT EXISTS batch_by_id_dfa 
    on public.dissemination_federalaward 
    using btree(api_v1_1_0_functions.batch(public.dissemination_federalaward.id));


NOTIFY pgrst, 'reload schema';
