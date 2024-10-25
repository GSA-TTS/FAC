-----------------------------------------------------------
-- general
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_general()
  RETURNS VOID
  AS
  $ct$
  BEGIN
  CREATE TABLE public_data_v1_0_0.general AS
    SELECT
      gen.id as id,
      NEXTVAL('public_data_v1_0_0.seq_general') AS seq,
      gen.report_id,
      gen.auditee_uei,
      gen.audit_year,
      gen.agencies_with_prior_findings,
      gen.audit_period_covered,
      gen.audit_type,
      gen.auditee_address_line_1,
      gen.auditee_certified_date,
      gen.auditee_certify_name,
      gen.auditee_certify_title,
      gen.auditee_city,
      gen.auditee_contact_name,
      gen.auditee_contact_title,
      gen.auditee_ein,
      gen.auditee_email,
      gen.auditee_name,
      gen.auditee_phone,
      gen.auditee_state,
      gen.auditee_zip,
      gen.auditor_address_line_1,
      gen.auditor_certified_date,
      gen.auditor_certify_name,
      gen.auditor_certify_title,
      gen.auditor_city,
      gen.auditor_contact_name,
      gen.auditor_contact_title,
      gen.auditor_country,
      gen.auditor_ein,
      gen.auditor_email,
      gen.auditor_firm_name,
      gen.auditor_foreign_address,
      gen.auditor_phone,
      gen.auditor_state,
      gen.auditor_zip,
      gen.cognizant_agency,
      gen.data_source,
      gen.date_created,
      gen.dollar_threshold,
      gen.entity_type,
      gen.fac_accepted_date,
      gen.fy_end_date,
      gen.fy_start_date,
      gen.gaap_results,
      gen.is_additional_ueis,
      gen.is_aicpa_audit_guide_included,
      gen.is_going_concern_included,
      gen.is_internal_control_deficiency_disclosed,
      gen.is_internal_control_material_weakness_disclosed,
      gen.is_low_risk_auditee,
      gen.is_material_noncompliance_disclosed,
      CASE EXISTS
        (
          SELECT 
            ein.report_id 
          FROM 
            dissemination_additionalein ein 
          WHERE 
          ein.report_id = gen.report_id
        )
        WHEN FALSE THEN 'No'
        ELSE 'Yes'
      END AS is_multiple_eins,
      gen.is_public,
      CASE EXISTS
        (
          SELECT 
            aud.report_id 
          FROM 
            dissemination_secondaryauditor aud 
          WHERE 
            aud.report_id = gen.report_id
        )
        WHEN FALSE THEN 'No'
        ELSE 'Yes'
      END AS is_secondary_auditors,
      gen.is_sp_framework_required,
      gen.number_months,
      gen.oversight_agency,
      gen.ready_for_certification_date,
      gen.sp_framework_basis,
      gen.sp_framework_opinions,
      gen.submitted_date,
      gen.total_amount_expended,
      gen.type_audit_code
    FROM
        dissem_copy.dissemination_general gen
    ORDER BY gen.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.general
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.general SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

DO LANGUAGE plpgsql
$GATE$
    DECLARE
        the_schema varchar := 'public_data_v1_0_0';
        the_table  varchar := 'metadata';
        api_ver    varchar := 'api_v2_0_0';
    BEGIN
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE  schemaname = the_schema
            AND    tablename  = the_table
            )
        THEN
            RAISE info '% Gate condition met. Skipping table creation.', api_ver;
        ELSE
            RAISE info '% %.% not found. Creating tables', api_ver, the_schema, the_table;
            RAISE info 'Creating general';
            PERFORM public_data_v1_0_0_functions.create_general();
        END IF;
    END
$GATE$;
