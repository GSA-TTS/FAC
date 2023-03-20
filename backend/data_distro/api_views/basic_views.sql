-- We are just pulling these views straight from the table

-- auditee
drop view if exists vw_auditee;
create view vw_auditee as select * from data_distro_auditee
    where data_distro_auditee.is_public=True;

-- auditor
drop view if exists vw_auditor;
create view vw_auditor as select * from data_distro_auditor
    where data_distro_auditor.is_public=True;

-- federal award
drop view if exists vw_federal_award;
-- will want to enhance this as a next step
create view vw_federal_award as select * from data_distro_federalaward
    where data_distro_federalaward.is_public=True;

-- CAP text
drop view if exists vw_cap_text;
create view vw_cap_text as select * from data_distro_captext
    where data_distro_captext.is_public=True;

-- note
drop view if exists vw_note;
create view vw_note as select * from data_distro_note
    where data_distro_note.is_public=True;

-- revision
drop view if exists vw_revision;
create view vw_revision as select * from data_distro_revision
    where data_distro_revision.is_public=True;

-- passthrough
drop view if exists vw_passthrough;
create view vw_passthrough as select * from data_distro_passthrough
    where data_distro_passthrough.is_public=True;
