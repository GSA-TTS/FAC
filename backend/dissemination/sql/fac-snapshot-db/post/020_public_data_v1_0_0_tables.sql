-----------------------------------------------------------
-- general
-----------------------------------------------------------
-- We do general first because all other tables are built off of it.
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


-----------------------------------------------------------
-- addition_eins
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_additional_eins()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.additional_eins AS
      SELECT 
        ein.id as id,
        NEXTVAL('public_data_v1_0_0.seq_additional_eins') AS seq,
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        gen.fac_accepted_date,
        ---
        ein.additional_ein
      FROM
          public_data_v1_0_0.general gen,
          dissem_copy.dissemination_additionalein ein
      WHERE
          gen.report_id = ein.report_id
      ORDER BY ein.id;

    ALTER TABLE public_data_v1_0_0.additional_eins
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.additional_eins SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;


-----------------------------------------------------------
-- additional_ueis
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_additional_ueis()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.additional_ueis AS
      SELECT
        uei.id as id,
        NEXTVAL('public_data_v1_0_0.seq_additional_ueis') AS seq,
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        gen.fac_accepted_date,
        ---
        uei.additional_uei
      FROM
        public_data_v1_0_0.general gen,
        dissem_copy.dissemination_additionaluei uei
      WHERE
        gen.report_id = uei.report_id
      ORDER BY uei.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.additional_ueis
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.additional_ueis SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- corrective_action_plans
-----------------------------------------------------------

CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_corrective_action_plans()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.corrective_action_plans AS
      SELECT
        cap.id as id,
        NEXTVAL('public_data_v1_0_0.seq_corrective_action_plans') as seq,
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        gen.fac_accepted_date,
        ---
        cap.contains_chart_or_table,
        cap.finding_ref_number,
        cap.planned_action
      FROM
        public_data_v1_0_0.general gen,
        dissem_copy.dissemination_captext cap
      WHERE
        cap.report_id = gen.report_id
        AND
        -- Only include the public corrective action plans.
        gen.is_public = true
      ORDER BY cap.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.corrective_action_plans
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.corrective_action_plans SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- federal_awards
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_federal_awards()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.federal_awards AS
      SELECT
        award.id as id,
        NEXTVAL('public_data_v1_0_0.seq_federal_awards') as seq,
        dg.report_id,
        dg.auditee_uei,
        dg.audit_year,
        dg.fac_accepted_date,
        concat(award.federal_agency_prefix,'.',award.federal_award_extension) as aln,
        ---
        award.additional_award_identification,
        award.amount_expended,
        award.audit_report_type,
        award.award_reference,
        award.cluster_name,
        award.cluster_total,
        award.federal_agency_prefix,
        award.federal_award_extension,
        award.federal_program_name,
        award.federal_program_total,
        award.findings_count,
        award.is_direct,
        award.is_loan,
        award.is_major,
        award.is_passthrough_award,
        award.loan_balance,
        award.other_cluster_name,
        award.passthrough_amount,
        award.state_cluster_name
      FROM
        public_data_v1_0_0.general dg,
        dissem_copy.dissemination_federalaward award
      WHERE
        award.report_id = dg.report_id
      ORDER BY award.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.federal_awards
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.federal_awards SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- findings
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_findings()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.findings AS
      SELECT
        finding.id as id,
        NEXTVAL('public_data_v1_0_0.seq_findings') as seq,
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        gen.fac_accepted_date,
        ---
        finding.award_reference,
        finding.is_material_weakness,
        finding.is_modified_opinion,
        finding.is_other_findings,
        finding.is_other_matters,
        finding.is_questioned_costs,
        finding.is_repeat_finding,
        finding.is_significant_deficiency,
        finding.prior_finding_ref_numbers,
        finding.reference_number,
        finding.type_requirement
      FROM
        public_data_v1_0_0.general gen,
        dissem_copy.dissemination_finding finding
      WHERE
        finding.report_id = gen.report_id
      ORDER BY finding.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.findings
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.findings SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- findings_text
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_findings_text()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.findings_text AS
      SELECT
        ft.id as id,
        NEXTVAL('public_data_v1_0_0.seq_findings_text') as seq,
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        gen.fac_accepted_date,
        ft.finding_ref_number,
        ft.contains_chart_or_table,
        ft.finding_text
      FROM
          public_data_v1_0_0.general gen,
          dissem_copy.dissemination_findingtext ft
      WHERE
          ft.report_id = gen.report_id
          AND
          gen.is_public = true
      ORDER BY ft.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.findings_text
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.findings_text SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- notes_to_sefa
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_notes_to_sefa()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.notes_to_sefa AS
      SELECT
        note.id as id,
        NEXTVAL('public_data_v1_0_0.seq_notes_to_sefa') as seq,
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        gen.fac_accepted_date,
        ---
        note.accounting_policies,
        note.contains_chart_or_table,
        note.content,
        note.is_minimis_rate_used,
        note.note_title as title,
        note.rate_explained
      FROM
          public_data_v1_0_0.general gen,
          dissem_copy.dissemination_note note
      WHERE
          note.report_id = gen.report_id
          AND
          -- Some notes are not public.
          gen.is_public = true
      ORDER BY note.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.notes_to_sefa
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.notes_to_sefa SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- passthrough
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_passthrough()
  RETURNS VOID
  AS
  $ct$
  BEGIN
  CREATE TABLE public_data_v1_0_0.passthrough AS
    SELECT
      pass.id as id,
      NEXTVAL('public_data_v1_0_0.seq_passthrough') as seq,
      gen.report_id,
      gen.auditee_uei,
      gen.audit_year,
      gen.fac_accepted_date,
      ---
      pass.award_reference,
      pass.passthrough_id,
      pass.passthrough_name
    FROM
        public_data_v1_0_0.general gen,
        dissem_copy.dissemination_passthrough pass
    WHERE
        gen.report_id = pass.report_id
    ORDER BY pass.id;

  -- Add a clean batch number after the table is created.
  ALTER TABLE public_data_v1_0_0.passthrough
  ADD COLUMN batch_number INTEGER;
  UPDATE public_data_v1_0_0.passthrough SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- secondary_auditors
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_secondary_auditors()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.secondary_auditors AS
      SELECT
        sa.id as id,
        NEXTVAL('public_data_v1_0_0.seq_secondary_auditors') as seq,
        gen.report_id,
        gen.auditee_uei,
        gen.audit_year,
        gen.fac_accepted_date,
        ---
        sa.address_city,
        sa.address_state,
        sa.address_street,
        sa.address_zipcode,
        sa.auditor_ein,
        sa.auditor_name,
        sa.contact_email,
        sa.contact_name,
        sa.contact_phone,
        sa.contact_title
      FROM
          public_data_v1_0_0.general gen,
          dissem_copy.dissemination_secondaryauditor sa
      WHERE
          sa.report_id = gen.report_id
      ORDER BY sa.id;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.secondary_auditors
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.secondary_auditors SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- combined
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_combined()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.combined AS
      SELECT
        dg.report_id,
        NEXTVAL('public_data_v1_0_0.seq_combined') as seq,
        dfa.award_reference,
        df.reference_number,
        concat(dfa.federal_agency_prefix,'.',dfa.federal_award_extension) as aln,
        --
        -- general
        --
        dg.id as general_row_id,
        dg.auditee_uei,
        dg.audit_year,
        dg.agencies_with_prior_findings,
        dg.audit_period_covered,
        dg.audit_type,
        dg.auditee_address_line_1,
        dg.auditee_certified_date,
        dg.auditee_certify_name,
        dg.auditee_certify_title,
        dg.auditee_city,
        dg.auditee_contact_name,
        dg.auditee_contact_title,
        dg.auditee_ein,
        dg.auditee_email,
        dg.auditee_name,
        dg.auditee_phone,
        dg.auditee_state,
        dg.auditee_zip,
        dg.auditor_address_line_1,
        dg.auditor_certified_date,
        dg.auditor_certify_name,
        dg.auditor_certify_title,
        dg.auditor_city,
        dg.auditor_contact_name,
        dg.auditor_contact_title,
        dg.auditor_country,
        dg.auditor_ein,
        dg.auditor_email,
        dg.auditor_firm_name,
        dg.auditor_foreign_address,
        dg.auditor_phone,
        dg.auditor_state,
        dg.auditor_zip,
        dg.cognizant_agency,
        dg.data_source,
        dg.date_created,
        dg.dollar_threshold,
        dg.entity_type,
        dg.fac_accepted_date,
        dg.fy_end_date,
        dg.fy_start_date,
        dg.gaap_results,
        dg.is_additional_ueis,
        dg.is_aicpa_audit_guide_included,
        dg.is_going_concern_included,
        dg.is_internal_control_deficiency_disclosed,
        dg.is_internal_control_material_weakness_disclosed,
        dg.is_low_risk_auditee,
        dg.is_material_noncompliance_disclosed,
        dg.is_multiple_eins,
        dg.is_public,
        dg.is_secondary_auditors,
        dg.is_sp_framework_required,
        dg.number_months,
        dg.oversight_agency,
        dg.ready_for_certification_date,
        dg.sp_framework_basis,
        dg.sp_framework_opinions,
        dg.submitted_date,
        dg.total_amount_expended,
        dg.type_audit_code,
        --
        -- federal_award
        --
        dfa.id as federal_award_row_id,
        dfa.additional_award_identification,
        dfa.amount_expended,
        dfa.audit_report_type,
        dfa.cluster_name,
        dfa.cluster_total,
        dfa.federal_agency_prefix,
        dfa.federal_award_extension,
        dfa.federal_program_name,
        dfa.federal_program_total,
        dfa.findings_count,
        dfa.is_direct,
        dfa.is_loan,
        dfa.is_major,
        dfa.is_passthrough_award,
        dfa.loan_balance,
        dfa.other_cluster_name,
        dfa.passthrough_amount,
        dfa.state_cluster_name,
        --
        -- finding
        --
        df.id as finding_row_id,
        df.is_material_weakness,
        df.is_modified_opinion,
        df.is_other_findings,
        df.is_other_matters,
        df.is_questioned_costs,
        df.is_repeat_finding,
        df.is_significant_deficiency,
        df.prior_finding_ref_numbers,
        df.type_requirement,
        --
        -- passthrough
        --
        dp.id as passthrough_row_id,
        dp.passthrough_id,
        dp.passthrough_name
      FROM 
        dissem_copy.dissemination_federalaward dfa
      LEFT JOIN public_data_v1_0_0.general dg 
        ON dfa.report_id = dg.report_id
      LEFT JOIN dissem_copy.dissemination_finding df 
        ON dfa.report_id = df.report_id 
        AND dfa.award_reference = df.award_reference
      LEFT JOIN dissem_copy.dissemination_passthrough dp
        ON dfa.report_id = dp.report_id 
        AND dfa.award_reference = dp.award_reference
      ORDER BY seq
      ;

      -- For advanced search, Django wants an `id` column.
      ALTER TABLE public_data_v1_0_0.combined
      ADD COLUMN id INTEGER;
      UPDATE public_data_v1_0_0.combined SET id=seq;

      -- Add a clean batch number after the table is created.
      ALTER TABLE public_data_v1_0_0.combined
      ADD COLUMN batch_number INTEGER;
      UPDATE public_data_v1_0_0.combined SET batch_number=DIV(seq, public.batch_size());
    END
    $ct$
    LANGUAGE plpgsql;

-----------------------------------------------------------
-- migration_inspection_record
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_migration_inspection_record()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.migration_inspection_record AS
      SELECT
        mir.id AS id,
        NEXTVAL('public_data_v1_0_0.seq_migration_inspection_record') as seq,
        mir.audit_year,
        mir.dbkey,
        mir.report_id,
        mir.run_datetime,
        mir.additional_ein,
        mir.additional_uei,
        mir.cap_text,
        mir.federal_award,
        mir.finding,
        mir.finding_text,
        mir.general,
        mir.note,
        mir.passthrough,
        mir.secondary_auditor
      FROM
        public_data_v1_0_0.general gen,
        dissem_copy.dissemination_migrationinspectionrecord mir
      WHERE
        mir.report_id = gen.report_id
        AND
        gen.is_public = true
      ;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.migration_inspection_record
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.migration_inspection_record SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- invalid_audit_record
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION public_data_v1_0_0_functions.create_invalid_audit_record()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE public_data_v1_0_0.invalid_audit_record AS
      SELECT
        iar.id AS id,
        NEXTVAL('public_data_v1_0_0.seq_invalid_audit_record') as seq,
        iar.audit_year,
        iar.dbkey,
        iar.report_id,
        iar.run_datetime,
        iar.additional_ein,
        iar.additional_uei,
        iar.cap_text,
        iar.federal_award,
        iar.finding,
        iar.finding_text,
        iar.general,
        iar.note,
        iar.passthrough,
        iar.secondary_auditor
      FROM
        dissem_copy.dissemination_invalidauditrecord iar,
        public_data_v1_0_0.general gen
      WHERE
        iar.report_id = gen.report_id
        AND
        gen.is_public = true
      ;

    -- Add a clean batch number after the table is created.
    ALTER TABLE public_data_v1_0_0.invalid_audit_record
    ADD COLUMN batch_number INTEGER;
    UPDATE public_data_v1_0_0.invalid_audit_record SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- CONDITIONAL TABLE CREATION
-- We make this conditional at startup/on deploy. 
-- The reason is that every time we deploy, this would tear down
-- the entire API, interrupting service. We only do that nightly, if we can.
-- However, on a clean deploy or a first deploy to a 2-DB config, we will
-- need this to run.
-----------------------------------------------------------
DO LANGUAGE plpgsql
$GO$
  BEGIN
    RAISE info 'Creating general';
    PERFORM public_data_v1_0_0_functions.create_general();
    RAISE info 'Creating additional_eins';
    PERFORM public_data_v1_0_0_functions.create_additional_eins();
    RAISE info 'Creating additional_ueis';
    PERFORM public_data_v1_0_0_functions.create_additional_ueis();
    RAISE info 'Creating corrective_action_plans';
    PERFORM public_data_v1_0_0_functions.create_corrective_action_plans();
    RAISE info 'Creating federal_awards';
    PERFORM public_data_v1_0_0_functions.create_federal_awards();
    RAISE info 'Creating findings';
    PERFORM public_data_v1_0_0_functions.create_findings();
    RAISE info 'Creating findings_text';
    PERFORM public_data_v1_0_0_functions.create_findings_text();
    RAISE info 'Creating notes_to_sefa';
    PERFORM public_data_v1_0_0_functions.create_notes_to_sefa();
    RAISE info 'Creating passthrough';
    PERFORM public_data_v1_0_0_functions.create_passthrough();
    RAISE info 'Creating secondary_auditors';
    PERFORM public_data_v1_0_0_functions.create_secondary_auditors();
    RAISE info 'Creating combined';
    PERFORM public_data_v1_0_0_functions.create_combined();
    RAISE info 'Creating migration_inspection_record';
    PERFORM public_data_v1_0_0_functions.create_migration_inspection_record();
    RAISE info 'Create invalid_audit_record';
    PERFORM public_data_v1_0_0_functions.create_invalid_audit_record();
  END
$GO$;
