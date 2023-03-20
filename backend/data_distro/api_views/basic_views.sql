-- We are just pulling these views straight from the table

-- auditee
create or replace view vw_general as
    select *
    from data_distro_auditee
    where data_distro_auditee.is_public=True
;

grant select on vw_general to anon;

-- auditor
create or replace view vw_auditor as
    select *
    from data_distro_auditor
    where data_distro_auditor.is_public=True
;

grant select on vw_auditor to anon;

-- federal award
-- will want to enhance this as a next step
create or replace view vw_federal_award as
    select *
    from data_distro_federalaward
    where data_distro_federalaward.is_public=True
;

grant select on vw_federal_award to anon;

-- CAP text
create or replace view vw_cap_text as
    select *
    from data_distro_captext
    where data_distro_captext.is_public=True
;

grant select on vw_cap_text to anon;

-- note
create or replace view vw_note as
    select *
    from data_distro_note
    where data_distro_note.is_public=True
;

grant select on vw_note to anon;

-- revision
create or replace view vw_revision as
    select *
    from data_distro_revision
    where data_distro_revision.is_public=True
;

grant select on vw_revision to anon;

-- passthrough
create or replace view vw_passthrough as
    select *
    from data_distro_passthrough
    where data_distro_passthrough.is_public=True
;

grant select on vw_passthrough to anon;
