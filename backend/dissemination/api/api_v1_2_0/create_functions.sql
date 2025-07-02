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


CREATE OR REPLACE FUNCTION api_v1_2_0_functions.get_header(item text) RETURNS text
    AS $get_header$
    declare res text;
   	begin
    	SELECT (current_setting('request.headers', true)::json)->>item into res;
    	return res;
   end;
$get_header$ LANGUAGE plpgsql;

create or replace function api_v1_2_0_functions.get_api_key_uuid() returns TEXT
as $gaku$
declare uuid text;
begin
	select api_v1_2_0_functions.get_header('x-api-user-id') into uuid;
	return uuid;
end;
$gaku$ LANGUAGE plpgsql;

create or replace function api_v1_2_0_functions.has_tribal_data_access()
returns boolean
as $has_tribal_data_access$
DECLARE
    uuid_header UUID;
    key_exists boolean;
BEGIN

    SELECT api_v1_2_0_functions.get_api_key_uuid() INTO uuid_header;
    SELECT
        CASE WHEN EXISTS (
            SELECT key_id
            FROM public.dissemination_TribalApiAccessKeyIds taaki
            WHERE taaki.key_id = uuid_header::TEXT)
            THEN 1::BOOLEAN
            ELSE 0::BOOLEAN
            END
        INTO key_exists;
    RAISE INFO 'api_v1_2_0 has_tribal % %', uuid_header, key_exists;
    RETURN key_exists;
END;
$has_tribal_data_access$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION api_v1_2_0.request_file_access(
    report_id TEXT
) RETURNS JSON LANGUAGE plpgsql AS
$$
DECLARE
    v_uuid_header TEXT;
    v_access_uuid VARCHAR(200);
    v_key_exists BOOLEAN;
    v_key_added_date DATE;
BEGIN

    SELECT api_v1_2_0_functions.get_api_key_uuid() INTO v_uuid_header;

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

NOTIFY pgrst, 'reload schema';
