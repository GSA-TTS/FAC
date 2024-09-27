
BEGIN;

    --
    -- We always tear everything down. Every time we create the public data,
    -- it is a complete refresh. So, rip out the schemas.
    --
    DROP SCHEMA IF EXISTS public_data_v1_0_0 CASCADE;
    
    --
    -- The teardown has to do some standup. Why? In this case, we're about to run
    -- `sling`. It will need to access some sequences to create the new tables with unique 
    -- row IDs. Those sequences need to exist before sling runs.
    --
    CREATE SCHEMA IF NOT EXISTS public_data_v1_0_0;

    -- 
    -- Sequences for the public tables.
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_general
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_additional_eins
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_additional_ueis
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_corrective_action_plans
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_federal_awards
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_findings
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_findings_text
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_notes_to_sefa
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_passthrough
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_secondary_auditors
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_combined
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;

COMMIT;

notify pgrst,
       'reload schema';
