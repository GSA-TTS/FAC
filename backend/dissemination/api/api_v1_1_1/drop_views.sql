begin;
    drop table if exists api_v1_1_1.metadata;
    drop table if exists dissemination_combined cascade;
    drop view if exists api_v1_1_1.general;
    drop view if exists api_v1_1_1.auditor;
    drop view if exists api_v1_1_1.federal_awards;
    drop view if exists api_v1_1_1.findings;
    drop view if exists api_v1_1_1.findings_text;
    drop view if exists api_v1_1_1.corrective_action_plans;
    drop view if exists api_v1_1_1.additional_ueis;
    drop view if exists api_v1_1_1.notes_to_sefa;
    drop view if exists api_v1_1_1.passthrough;
    drop view if exists api_v1_1_1.secondary_auditors;
    drop view if exists api_v1_1_1.additional_eins;
    drop view if exists api_v1_1_1.combined cascade;
commit;

notify pgrst,
       'reload schema';
