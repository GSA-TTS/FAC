begin;

    drop table if exists api_v1_0_1.metadata;
    drop view if exists api_v1_0_1.general;
    drop view if exists api_v1_0_1.auditor;
    drop view if exists api_v1_0_1.federal_award;
    drop view if exists api_v1_0_1.finding;
    drop view if exists api_v1_0_1.finding_text;
    drop view if exists api_v1_0_1.cap_text;
    drop view if exists api_v1_0_1.note;

commit;

notify pgrst,
       'reload schema';
