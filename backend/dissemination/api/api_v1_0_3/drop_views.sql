begin;
    drop table if exists api_v1_0_3.metadata;
    drop view if exists api_v1_0_3.general;
    drop view if exists api_v1_0_3.auditor;
    drop view if exists api_v1_0_3.federal_awards;
    drop view if exists api_v1_0_3.findings;
    drop view if exists api_v1_0_3.findings_text;
    drop view if exists api_v1_0_3.corrective_action_plans;
    drop view if exists api_v1_0_3.additional_ueis;
    drop view if exists api_v1_0_3.notes_to_sefa;
    drop view if exists api_v1_0_3.passthrough;
    drop view if exists api_v1_0_3.secondary_auditors;
    drop view if exists api_v1_0_3.additional_eins;
commit;

notify pgrst,
       'reload schema';
