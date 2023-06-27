
begin;

drop view if exists api.vw_general;
create view api.vw_general as
    select gen.*
    from dissemination_General gen
    where gen.is_public=True
;

drop view if exists api.vw_federal_award;
create view api.vw_federal_award as
    select gen.uei, gen.audit_year, award.*
    from dissemination_General gen,
         dissemination_FederalAward award
    where gen.is_public=True
      and gen.report_id = award.report_id    
;

drop view if exists api.vw_finding;
create view api.vw_finding as
    select gen.uei, gen.audit_year, finding.*
    from dissemination_General gen,
         dissemination_Finding finding
    where gen.is_public=True
      and gen.report_id = finding.report_id    
;

commit;

notify pgrst,
       'reload schema';

