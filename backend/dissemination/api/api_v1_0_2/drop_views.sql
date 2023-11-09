begin;

    drop table if exists api_v1_0_2.metadata;
    drop view if exists api_v1_0_2.general;
    drop view if exists api_v1_0_2.auditor;
    drop view if exists api_v1_0_2.federal_award;
    drop view if exists api_v1_0_2.finding;
    drop view if exists api_v1_0_2.finding_text;
    drop view if exists api_v1_0_2.cap_text;
    drop view if exists api_v1_0_2.note;

commit;

notify pgrst,
       'reload schema';
