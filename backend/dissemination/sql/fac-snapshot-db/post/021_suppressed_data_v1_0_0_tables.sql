-----------------------------------------------------------
-- corrective_action_plans
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_corrective_action_plans()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE suppressed_data_v1_0_0.corrective_action_plans AS
      SELECT
        cap.id as id,
        NEXTVAL('suppressed_data_v1_0_0.seq_corrective_action_plans') as seq,
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
        -- Only include the suppressed corrective action plans.
        gen.is_public = false
      ORDER BY cap.id;
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- findings_text
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_findings_text()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE suppressed_data_v1_0_0.findings_text AS
      SELECT
        ft.id as id,
        NEXTVAL('suppressed_data_v1_0_0.seq_findings_text') as seq,
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
          -- Findings text is not always public
          gen.is_public = false
      ORDER BY ft.id;
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- notes_to_sefa
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_notes_to_sefa()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE suppressed_data_v1_0_0.notes_to_sefa AS
      SELECT
        note.id as id,
        NEXTVAL('suppressed_data_v1_0_0.seq_notes_to_sefa') as seq,
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
          gen.is_public = false
      ORDER BY note.id;
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- migration_inspection_record
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_migration_inspection_record()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE suppressed_data_v1_0_0.migration_inspection_record AS
      SELECT
        mir.id AS id,
        NEXTVAL('suppressed_data_v1_0_0.seq_migration_inspection_record') as seq,
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
        gen.is_public = false
      ;

    -- Add a clean batch number after the table is created.
    ALTER TABLE suppressed_data_v1_0_0.migration_inspection_record
    ADD COLUMN batch_number INTEGER;
    UPDATE suppressed_data_v1_0_0.migration_inspection_record SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- invalid_audit_record
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_invalid_audit_record()
  RETURNS VOID
  AS
  $ct$
  BEGIN
    CREATE TABLE suppressed_data_v1_0_0.invalid_audit_record AS
      SELECT
        iar.id AS id,
        NEXTVAL('suppressed_data_v1_0_0.seq_invalid_audit_record') as seq,
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
        dissem_copy.dissemination_general gen
      WHERE
        iar.report_id = gen.report_id
        AND
        gen.is_public = true
      ;

    -- Add a clean batch number after the table is created.
    ALTER TABLE suppressed_data_v1_0_0.invalid_audit_record
    ADD COLUMN batch_number INTEGER;
    UPDATE suppressed_data_v1_0_0.invalid_audit_record SET batch_number=DIV(seq, public.batch_size());
  END
  $ct$
  LANGUAGE plpgsql;

-----------------------------------------------------------
-- CONDITIONAL TABLE CREATION
-----------------------------------------------------------
DO LANGUAGE plpgsql
$GO$
  BEGIN
    RAISE info 'Creating suppressed corrective_action_plans';
    PERFORM suppressed_data_v1_0_0.create_corrective_action_plans();
    RAISE info 'Creating suppressed findings_text';
    PERFORM suppressed_data_v1_0_0.create_findings_text();
    RAISE info 'Creating suppressed notes_to_sefa';
    PERFORM suppressed_data_v1_0_0.create_notes_to_sefa();
    RAISE info 'Creating migration_inspection_record';
    PERFORM suppressed_data_v1_0_0.create_migration_inspection_record();
    RAISE info 'Create invalid_audit_record';
    PERFORM suppressed_data_v1_0_0.create_invalid_audit_record();
  END
$GO$;
