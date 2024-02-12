begin;
    drop table if exists api_v1_1_0.metadata;
    drop view if exists api_v1_1_0.general;
    drop view if exists api_v1_1_0.auditor;
    drop view if exists api_v1_1_0.federal_awards;
    drop view if exists api_v1_1_0.findings;
    drop view if exists api_v1_1_0.findings_text;
    drop view if exists api_v1_1_0.corrective_action_plans;
    drop view if exists api_v1_1_0.additional_ueis;
    drop view if exists api_v1_1_0.notes_to_sefa;
    drop view if exists api_v1_1_0.passthrough;
    drop view if exists api_v1_1_0.secondary_auditors;
    drop view if exists api_v1_1_0.additional_eins;
commit;

notify pgrst,
       'reload schema';
