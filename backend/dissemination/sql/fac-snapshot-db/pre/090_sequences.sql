-- Sequences are used to provide a foundation for batching, which
-- is needed for fast download of data. 
----------------------------------------------------------
-- PUBLIC DATA TABLES
----------------------------------------------------------
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_additional_eins;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_additional_ueis;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_combined;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_corrective_action_plans;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_federal_awards;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_findings_text;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_findings;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_general;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_notes_to_sefa;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_passthrough;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_secondary_auditors;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_migration_inspection_record;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_invalid_audit_record;

CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_additional_eins               START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_additional_ueis               START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_combined                      START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_corrective_action_plans       START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_federal_awards                START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_findings_text                 START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_findings                      START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_general                       START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_notes_to_sefa                 START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_passthrough                   START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_secondary_auditors            START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_migration_inspection_record   START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_invalid_audit_record          START 1;

----------------------------------------------------------
-- SUPPRESSED DATA TABLES
----------------------------------------------------------
DROP SEQUENCE IF EXISTS suppressed_data_v1_0_0.seq_corrective_action_plans;
DROP SEQUENCE IF EXISTS suppressed_data_v1_0_0.seq_findings_text;
DROP SEQUENCE IF EXISTS suppressed_data_v1_0_0.seq_notes_to_sefa;
DROP SEQUENCE IF EXISTS suppressed_data_v1_0_0.seq_migration_inspection_record;
DROP SEQUENCE IF EXISTS suppressed_data_v1_0_0.seq_invalid_audit_record;

CREATE SEQUENCE IF NOT EXISTS suppressed_data_v1_0_0.seq_corrective_action_plans       START 1;
CREATE SEQUENCE IF NOT EXISTS suppressed_data_v1_0_0.seq_findings_text                 START 1;
CREATE SEQUENCE IF NOT EXISTS suppressed_data_v1_0_0.seq_notes_to_sefa                 START 1;
CREATE SEQUENCE IF NOT EXISTS suppressed_data_v1_0_0.seq_migration_inspection_record   START 1;
CREATE SEQUENCE IF NOT EXISTS suppressed_data_v1_0_0.seq_invalid_audit_record          START 1;
