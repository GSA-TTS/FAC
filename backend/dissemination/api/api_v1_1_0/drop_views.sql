begin;

    drop table if exists api_v1_1_0.metadata;
    drop view if exists api_v1_1_0.general;
    drop view if exists api_v1_1_0.auditor;
    drop view if exists api_v1_1_0.federal_award;
    drop view if exists api_v1_1_0.finding;
    drop view if exists api_v1_1_0.finding_text;
    drop view if exists api_v1_1_0.cap_text;
    drop view if exists api_v1_1_0.note;

commit;

notify pgrst,
       'reload schema';
