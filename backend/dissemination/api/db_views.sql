
begin;

drop view if exists api.vw_general;
create view api.vw_general as
    select gen.*
    from dissemination_General gen
    where gen.is_public=True
;

commit;

notify pgrst,
       'reload schema';

