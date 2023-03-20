-- We are just pulling these views straight from the table

create view vw_auditee as select * from data_distro_auditee
    where data_distro_auditee.is_public=True;

create view vw_auditor as select * from data_distro_auditor
    where data_distro_auditor.is_public=True;

-- will want to enhance this as a next step
create view vw_federal_award as select * from data_distro_federalaward
    where data_distro_federalaward.is_public=True;

-- may want to add this to findings
create view vw_cap_text as select * from data_distro_captext
    where data_distro_captext.is_public=True;

create view vw_note as select * from data_distro_note
    where data_distro_note.is_public=True;

create view vw_revision as select * from data_distro_revision
    where data_distro_revision.is_public=True;

create view vw_passthrough as select * from data_distro_passthrough
    where data_distro_passthrough.is_public=True;
