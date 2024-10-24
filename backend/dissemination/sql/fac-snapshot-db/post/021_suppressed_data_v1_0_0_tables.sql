-----------------------------------------------------------
-- general
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_corrective_action_plans()
  RETURNS VOID
AS
$ct$
BEGIN
  CREATE TABLE suppressed_data_v1_0_0.corrective_action_plans AS
    SELECT
      cap.id as id,
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
      copy.dissemination_captext cap
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
-- general
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_findings_text()
  RETURNS VOID
AS
$ct$
BEGIN
  CREATE TABLE suppressed_data_v1_0_0.findings_text AS
    SELECT
      ft.id as id,
      gen.report_id,
      gen.auditee_uei,
      gen.audit_year,
      gen.fac_accepted_date,
      ft.finding_ref_number,
      ft.contains_chart_or_table,
      ft.finding_text
    FROM
        public_data_v1_0_0.general gen,
        copy.dissemination_findingtext ft
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
-- general
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION suppressed_data_v1_0_0.create_notes_to_sefa()
  RETURNS VOID
AS
$ct$
BEGIN
  CREATE TABLE suppressed_data_v1_0_0.notes_to_sefa AS
    SELECT
      note.id as id,
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
        copy.dissemination_note note
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
-- CONDITIONAL TABLE CREATION
-- We make this conditional at startup/on deploy. 
-- The reason is that every time we deploy, this would tear down
-- the entire API, interrupting service. We only do that nightly, if we can.
-- However, on a clean deploy or a first deploy to a 2-DB config, we will
-- need this to run.
-----------------------------------------------------------
DO LANGUAGE plpgsql
$GATE$
    DECLARE
        the_schema varchar := 'public_data_v1_0_0';
        the_table  varchar := 'metadata';
    BEGIN
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE  schemaname = the_schema
            AND    tablename  = the_table
            )
        THEN
            RAISE info 'Found the metadata table; skipping suppressed data table creation.';
        ELSE
            RAISE info 'Metadata table not found. Creating suppressed data tables.';
            RAISE info 'Creating suppressed corrective_action_plans';
            PERFORM suppressed_data_v1_0_0.create_corrective_action_plans();
            RAISE info 'Creating suppressed findings_text';
            PERFORM suppressed_data_v1_0_0.create_findings_text();
            RAISE info 'Creating suppressed notes_to_sefa';
            PERFORM suppressed_data_v1_0_0.create_notes_to_sefa();
        END IF;
    END
$GATE$;
