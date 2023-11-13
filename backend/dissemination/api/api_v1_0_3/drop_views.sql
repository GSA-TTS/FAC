begin;

    drop table if exists api_v1_0_3.metadata;
    drop view if exists api_v1_0_3.general;
    drop view if exists api_v1_0_3.auditor;
    drop view if exists api_v1_0_3.federal_award;
    drop view if exists api_v1_0_3.finding;
    drop view if exists api_v1_0_3.finding_text;
    drop view if exists api_v1_0_3.cap_text;
    drop view if exists api_v1_0_3.note;

commit;

notify pgrst,
       'reload schema';
