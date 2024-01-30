CREATE OR REPLACE FUNCTION api_v1_0_3_functions.request_file_access(
    p_report_id INTEGER,
    p_api_key_id INTEGER
) RETURNS JSON LANGUAGE plpgsql AS
$$
DECLARE
    v_access_uuid VARCHAR(32);
    v_has_permission BOOLEAN;
    v_key_exists BOOLEAN;
    v_key_added_date DATE;
BEGIN
    -- Check if the user has tribal data access permission
    SELECT api_v1_0_3_functions.has_tribal_data_access() INTO v_has_permission;

    -- Check if the provided API key exists in public.dissemination_TribalApiAccessKeyIds
    SELECT 
        EXISTS(
            SELECT 1
            FROM public.dissemination_TribalApiAccessKeyIds
            WHERE keyid = p_api_key_id
        ) INTO v_key_exists;

    -- Get the added date of the key from public.dissemination_TribalApiAccessKeyIds
    SELECT date_added
    INTO v_key_added_date
    FROM public.dissemination_TribalApiAccessKeyIds
    WHERE keyid = p_api_key_id;

    -- Check if the key is less than 6 months old
    IF p_api_key_id IS NOT NULL AND v_has_permission AND v_key_exists AND v_key_added_date >= CURRENT_DATE - INTERVAL '6 months' THEN
        -- Generate UUID (using PostgreSQL's gen_random_uuid function)
        SELECT REPLACE(gen_random_uuid()::text, '-', '') INTO v_access_uuid;

        -- Inserting data into the one_time_access table
        INSERT INTO public.dissemination_onetimeaccess (uuid, api_key_id, report_id)
        VALUES (v_access_uuid, p_api_key_id, p_report_id);

        -- Return the UUID to the user
        RETURN json_build_object('access_uuid', v_access_uuid);
    ELSE
        -- Return an error for unauthorized access
        RETURN json_build_object('error', 'Unauthorized access or key older than 6 months')::JSON;
    END IF;
END;
$$;
