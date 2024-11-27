CREATE OR REPLACE FUNCTION api_v2_0_0.request_file_access(
    report_id TEXT
) RETURNS JSON LANGUAGE plpgsql AS
$$
DECLARE
    v_uuid_header TEXT;
    v_access_uuid VARCHAR(200);
    v_key_exists BOOLEAN;
    v_key_added_date DATE;
BEGIN
    
    SELECT api_v2_0_0_functions.get_api_key_uuid() INTO v_uuid_header;

    -- Check if the provided API key exists in dissem_copy.dissemination_TribalApiAccessKeyIds
    SELECT 
        EXISTS(
            SELECT 1
            FROM dissem_copy.dissemination_tribalapiaccesskeyids
            WHERE key_id = v_uuid_header
        ) INTO v_key_exists;
    

    -- Get the added date of the key from dissem_copy.dissemination_TribalApiAccessKeyIds
    SELECT date_added
    INTO v_key_added_date
    FROM dissem_copy.dissemination_tribalapiaccesskeyids
    WHERE key_id = v_uuid_header;
    

    -- Check if the key is less than 6 months old
    IF v_uuid_header IS NOT NULL AND v_key_exists AND v_key_added_date >= CURRENT_DATE - INTERVAL '6 months' THEN
        -- Generate UUID (using PostgreSQL's gen_random_uuid function)
        SELECT gen_random_uuid() INTO v_access_uuid;  
              
        -- Inserting data into the one_time_access table
        INSERT INTO dissem_copy.dissemination_onetimeaccess (uuid, api_key_id, timestamp, report_id)
        VALUES (v_access_uuid::UUID, v_uuid_header, CURRENT_TIMESTAMP, report_id);

        -- Return the UUID to the user
        RETURN json_build_object('access_uuid', v_access_uuid);
    ELSE
        -- Return an error for unauthorized access
        RETURN json_build_object('error', 'Unauthorized access or key older than 6 months')::JSON;
    END IF;
END;
$$;
