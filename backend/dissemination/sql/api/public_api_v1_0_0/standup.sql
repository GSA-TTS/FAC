------------------------------------------------------------------
-- GATE
------------------------------------------------------------------
-- We only want the API to run if certain conditions are met.
-- We could try and encode that in the `bash` portion of the code.
-- Or, we could just gate things at the top of our SQL. 
-- If the conditions are not met, we should exit noisily.
-- A cast to regclass will fail with an exception if the table
-- does not exist.
DO LANGUAGE plpgsql
$GATE$
    DECLARE
        the_schema varchar := 'public_data_v1_0_0';
        the_table  varchar := 'metadata';
        api_ver    varchar := 'PUBLIC_V1_0_0';
    BEGIN
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE  schemaname = the_schema
            AND    tablename  = the_table
            )
        THEN
            RAISE info '% Gate condition met. Continuing.', api_ver;
        ELSE
            RAISE exception '% %.% not found.', api_ver, the_schema, the_table;
        END IF;
    END
$GATE$;
-----------------------------------------------------
-- PERMISSIONS
-----------------------------------------------------
do
$$
BEGIN
    DROP SCHEMA IF EXISTS public_api_v1_0_0 CASCADE;
    DROP SCHEMA IF EXISTS public_api_v1_0_0_functions CASCADE;
    CREATE SCHEMA IF NOT EXISTS public_api_v1_0_0;
    CREATE SCHEMA IF NOT EXISTS public_api_v1_0_0_functions;
    -- Functions are loaded before sling comes up.
        
    GRANT USAGE ON SCHEMA public_api_v1_0_0_functions TO api_fac_gov;
    GRANT USAGE ON SCHEMA public_api_v1_0_0 TO api_fac_gov;
    GRANT USAGE ON SCHEMA public_data_v1_0_0 TO api_fac_gov;

END
$$
;

---
-- FUNCTIONS
--

CREATE OR REPLACE FUNCTION public_api_v1_0_0_functions.rows_per_batch()
    RETURNS integer
    LANGUAGE sql IMMUTABLE PARALLEL SAFE AS
    'SELECT 20000';

CREATE OR REPLACE FUNCTION public_api_v1_0_0_functions.batch (id bigint) 
    RETURNS bigint
    AS $batch$
    DECLARE result bigint;
    DECLARE RPB integer;
    BEGIN 
        SELECT public_api_v1_0_0_functions.rows_per_batch() INTO RPB;
        SELECT div(id, RPB) INTO result;
        RETURN result;
    END
    $batch$
    LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION public_api_v1_0_0_functions.batches (_table text) 
returns integer 
as $batches$
declare 
    count integer;
    RPB integer;
begin 
    select public_api_v1_0_0_functions.rows_per_batch() into RPB;
	case
	   	when _table = 'additional_eins' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.additional_eins;
	   	when _table = 'additional_ueis' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.additional_ueis;
	   	when _table = 'combined' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.combined;
	   	when _table = 'corrective_action_plans' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.corrective_action_plans;
	   	when _table = 'federal_awards' then
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.federal_awards;
	   	when _table = 'findings_text' then
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.findings_text;
	   	when _table = 'findings' then
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.findings;
	   	when _table = 'general' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.general;
	   	when _table = 'notes_to_sefa' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.notes_to_sefa;
	   	when _table = 'passthrough' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.passthrough;
	   	when _table = 'secondary_auditors' then  
	   		select div(count(*), RPB) into count 
	   		from public_data_v1_0_0.secondary_auditors;
	else
		count := 0;
	end case;
	RETURN count;
end
$batches$   
language plpgsql;

CREATE OR REPLACE FUNCTION public_api_v1_0_0.compute_batch(row_id bigint)
    RETURNS BIGINT
    AS $$
        DECLARE result bigint;
        BEGIN
            SELECT public_api_v1_0_0_functions.batch(row_id) INTO result;
            return result;
        END
    $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION public_api_v1_0_0.get_batch_additional_eins (_batch bigint) 
RETURNS SETOF record
AS $get_batch$
BEGIN
    RETURN QUERY SELECT * 
    FROM public_data_v1_0_0.additional_eins 
    WHERE batch_number = _batch;
END;
$get_batch$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public_api_v1_0_0.get_batch_federal_awards (_batch bigint) 
RETURNS SETOF public_data_v1_0_0.federal_awards
AS $get_batch$
BEGIN
    RETURN QUERY SELECT * 
    FROM public_data_v1_0_0.federal_awards
    WHERE batch_number = _batch;
END;
$get_batch$
LANGUAGE plpgsql;

NOTIFY pgrst, 'reload schema';


-- 	   	when _table = 'additional_ueis' then  
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.additional_ueis 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'combined' then  
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.combined 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'corrective_action_plans' then  
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.corrective_action_plans 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'federal_awards' then
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.federal_awards 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'findings_text' then
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.findings_text 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'findings' then
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.findings 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'general' then  
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.general 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'notes_to_sefa' then  
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.notes_to_sefa 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'passthrough' then  
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.passthrough 
--             WHERE batch_number = _batch;
-- 	   	when _table = 'secondary_auditors' then  
-- 	   		RETURN QUERY SELECT * 
--             FROM public_data_v1_0_0.secondary_auditors 
--             WHERE batch_number = _batch;
-- 	end case;
-- END;
-- $get_batch$   
-- language plpgsql;


NOTIFY pgrst, 'reload schema';

BEGIN;

CREATE VIEW public_api_v1_0_0.additional_eins AS
    SELECT * FROM public_data_v1_0_0.additional_eins ae
    ORDER BY ae.id
;

---------------------------------------
-- additional_ueis
---------------------------------------
create view public_api_v1_0_0.additional_ueis AS
    SELECT * FROM public_data_v1_0_0.additional_ueis au
    ORDER BY au.id
;

---------------------------------------
-- corrective_action_plan
---------------------------------------
CREATE VIEW public_api_v1_0_0.corrective_action_plans AS
    SELECT * FROM public_data_v1_0_0.corrective_action_plans cap
    ORDER BY cap.id
;

---------------------------------------
-- finding
---------------------------------------
CREATE VIEW public_api_v1_0_0.findings as
    SELECT * FROM public_data_v1_0_0.findings f
    ORDER BY f.id
;

---------------------------------------
-- finding_text
---------------------------------------
CREATE VIEW public_api_v1_0_0.findings_text AS
    SELECT * FROM public_data_v1_0_0.findings_text ft
    ORDER BY ft.id
;

---------------------------------------
-- federal award
---------------------------------------
CREATE VIEW public_api_v1_0_0.federal_awards AS
    SELECT * FROM public_data_v1_0_0.federal_awards fa
    ORDER BY fa.id
;

---------------------------------------
-- general
---------------------------------------
CREATE VIEW public_api_v1_0_0.general AS
    SELECT * FROM public_data_v1_0_0.general
;

---------------------------------------
-- notes_to_sefa
---------------------------------------
create view public_api_v1_0_0.notes_to_sefa AS
    SELECT * FROM public_data_v1_0_0.notes_to_sefa nts
    ORDER BY nts.id
;

---------------------------------------
-- passthrough
---------------------------------------
CREATE VIEW public_api_v1_0_0.passthrough AS
    SELECT * FROM public_data_v1_0_0.passthrough p
    ORDER BY p.id
;

---------------------------------------
-- auditor (secondary auditor)
---------------------------------------
CREATE VIEW public_api_v1_0_0.secondary_auditors AS
    SELECT * FROM public_data_v1_0_0.secondary_auditors sa
    ORDER BY sa.id
    ;

---------------------------------------
-- combined
---------------------------------------
CREATE VIEW public_api_v1_0_0.combined AS
    SELECT * FROM public_data_v1_0_0.combined comb
    ;

---------------------------------------
-- metadata
---------------------------------------
CREATE VIEW public_api_v1_0_0.metadata AS
    SELECT * FROM public_data_v1_0_0.metadata
    ;
