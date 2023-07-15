begin;

    drop table if exists api_v1_0_0_beta.metadata;
    drop view if exists api_v1_0_0_beta.general;
    drop view if exists api_v1_0_0_beta.auditor;
    drop view if exists api_v1_0_0_beta.federal_award;
    drop view if exists api_v1_0_0_beta.finding;
    drop view if exists api_v1_0_0_beta.finding_text;
    drop view if exists api_v1_0_0_beta.cap_text;
    drop view if exists api_v1_0_0_beta.note;

commit;

notify pgrst,
       'reload schema';