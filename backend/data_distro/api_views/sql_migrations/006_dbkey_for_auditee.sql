-- Adding dbkey auditee
drop view if exists api.vw_auditee;
create view api.vw_auditee as
with auditee as (
    select *
    from data_distro_auditee
    where data_distro_auditee.is_public=True
),
gen as (
    select distinct auditee_id as auditee_id, array_agg(id) as general_id
    from data_distro_general
    group by auditee_id
),
db as(
    select distinct auditee_id, array_agg(dbkey) as dbkey
    from data_distro_general
    group by auditee_id
)
select auditee.*, gen.general_id, db.dbkey
from auditee
left join gen on gen.auditee_id=auditee.id
left join db on db.auditee_id=auditee.id
;