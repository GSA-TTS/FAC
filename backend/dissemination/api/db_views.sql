
begin;

drop view if exists api.vw_general;
create view api.vw_general as
    select gen.*, ga.*
    from dissemination_General gen
    left outer join GenAuditor ga on ga.report_id = gen.report_id
    where gen.is_public=True
;

drop view if exists api.vw_federal_award;
create view api.vw_federal_award as
    select gen.uei, gen.audit_year, award.*
    from dissemination_FederalAward award
    left join dissemination_General gen on award.report_id = gen.report_id
    where gen.is_public=True
;

drop view if exists api.vw_finding;
create view api.vw_finding as
    select gen.uei, gen.audit_year, 
          award.award_seq_number, award.federal_agency_prefix, award.federal_award_extension, 
          finding.*
    from dissemination_Finding finding
    left join dissemination_FederalAward award on award.award_seq_number = finding.award_seq_number
    left join dissemination_General gen on award.report_id = gen.report_id
    where gen.is_public=True
      and gen.report_id = finding.report_id    
;
drop view if exists api.vw_finding_text;
create view api.vw_finding_text as
    select gen.uei, gen.audit_year, 
          -- award.award_seq_number, award.federal_agency_prefix, award.federal_award_extension, 
          ft.*
    from dissemination_FindingText ft
    left join dissemination_General gen on ft.report_id = gen.report_id
    -- TODO fix join columns
    -- left join dissemination_Finding finding on award.award_seq_number = finding.award_seq_number
    -- left join dissemination_FederalAward award on award.award_seq_number = finding.award_seq_number
    where gen.is_public=True
;

commit;

notify pgrst,
       'reload schema';

