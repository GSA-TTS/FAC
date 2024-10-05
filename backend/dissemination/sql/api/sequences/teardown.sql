-- We need these sequences for bringing the public tables back.
-- That is, sling needs them. So, lets build them right now.
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_additional_eins;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_additional_ueis;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_combined;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_corrective_action_plans;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_federal_awards;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_findings_text;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_findings;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_general;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_notes_to_sefa;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_passthrough;
DROP SEQUENCE IF EXISTS public_data_v1_0_0.seq_v1_0_0_secondary_auditors;

CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_additional_eins         START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_additional_ueis         START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_combined                START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_corrective_action_plans START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_federal_awards          START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_findings_text           START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_findings                START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_general                 START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_notes_to_sefa           START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_passthrough             START 1;
CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_v1_0_0_secondary_auditors      START 1;
