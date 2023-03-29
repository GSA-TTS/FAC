-- run by data/distro/migrations/0030_add_api_views.py
-- rerun in data/distro/migrations/0032_update_API.py (needed to recreate view but no new SQL was needed)

-- Current script to recreate views

begin;

-- auditee
drop view if exists api.vw_auditee;
create view api.vw_auditee as
with auditee as (
    select *
    from data_distro_auditee
    where data_distro_auditee.is_public=True
),
gen as(
    select id as general_id, auditee_id
    from data_distro_general
)
select auditee.*, gen.general_id
from auditee
left join gen on gen.auditee_id=auditee.id
;


-- auditor
drop view if exists api.vw_auditor;
create view api.vw_auditor as
with auditor as (
    select *
    from data_distro_auditor
    where data_distro_auditor.is_public=True
),
gen as (
    select distinct primary_auditor_id, array_agg(id) as general_id
    from data_distro_general
    group by primary_auditor_id
),
gen_secondary as (
    select distinct auditor_id as auditor_id,
        array_agg(general_id) as secondary_auditor_general_id
    from data_distro_general_secondary_auditors
    group by auditor_id
)
select auditor.*, gen.general_id, gen_secondary.secondary_auditor_general_id
from auditor
left join gen on gen.primary_auditor_id=auditor.id
left join gen_secondary on gen_secondary.auditor_id=auditor.id
;


-- federal award
-- might want to add more links to related objects as a next step
drop view if exists api.vw_federal_award;
create view api.vw_federal_award as
with fed_award as (
    select *
    from data_distro_federalaward
    where data_distro_federalaward.is_public=True
),
gen as (
    select distinct federalaward_id as federal_award_id, array_agg(id) as general_id
    from data_distro_general_federal_awards
    group by federal_award_id
)
select fed_award.*, gen.general_id
from fed_award
left join gen on fed_award.id=gen.federal_award_id
;


-- CAP text
drop view if exists api.vw_cap_text;
create view api.vw_cap_text as
with captext as (
    select *
    from data_distro_captext
    where data_distro_captext.is_public=True
),
gen as (
    select distinct captext_id, array_agg(general_id) as general_id
    from data_distro_general_cap_text
    group by captext_id
)
select captext.*, gen.general_id
from captext
left join gen on captext.id=gen.captext_id
;


-- note
drop view if exists api.vw_note;
create view api.vw_note as
with note as(
    select *
    from data_distro_note
    where data_distro_note.is_public=True
),
gen as (
    select distinct note_id, array_agg(general_id) as general_id
    from data_distro_general_notes
    group by note_id
)
select note.*, gen.general_id
from note
left join gen on note.id=gen.note_id
;


-- revision
drop view if exists api.vw_revision;
create view api.vw_revision as
with revision as(
    select *
    from data_distro_revision
    where data_distro_revision.is_public=True
),
gen as (
    select distinct revision_id, array_agg(id) as general_id
    from data_distro_general
    group by revision_id
)
select revision.*, gen.general_id
from revision
left join gen on revision.id=gen.revision_id
;


-- passthrough
drop view if exists api.vw_passthrough;
create view api.vw_passthrough as
with pass as(
    select *
    from data_distro_passthrough
    where data_distro_passthrough.is_public=True
),
gen as (
    select distinct passthrough_id, array_agg(general_id) as general_id
    from data_distro_general_passthrough
    group by passthrough_id
)
select pass.*, gen.general_id
from pass
left join gen on pass.id=gen.passthrough_id
;

commit;
