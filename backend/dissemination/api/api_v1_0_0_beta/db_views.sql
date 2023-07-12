
begin;

drop view if exists api_v1_0_0_beta.general;
create view api_v1_0_0_beta.general as
    select gen.*, 
          award.federal_agency_prefix, award.federal_award_extension
    from dissemination_General gen
    left outer join dissemination_FederalAward award on gen.report_id = award.report_id
    where gen.is_public=True
;

drop view if exists api.vw_auditor;
create view api.vw_auditor as
    select gen.auditee_uei, gen.auditee_ein, gen.audit_year,
           ga.*
    from dissemination_GenAuditor ga
    left join dissemination_General gen on ga.report_id = gen.report_id
    where gen.is_public=True
;

drop view if exists api_v1_0_0_beta.federal_award;
create view api_v1_0_0_beta.federal_award as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, award.*
    from dissemination_FederalAward award
    left join dissemination_General gen on award.report_id = gen.report_id
    where gen.is_public=True
;

drop view if exists api_v1_0_0_beta.finding;
create view api_v1_0_0_beta.finding as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, 
          award.federal_agency_prefix, award.federal_award_extension, 
          finding.*
    from dissemination_Finding finding
    left join dissemination_FederalAward award 
        on award.report_id = finding.report_id 
          and award.award_seq_number = finding.award_seq_number
    left join dissemination_General gen on award.report_id = gen.report_id
    where gen.is_public=True
;

drop view if exists api_v1_0_0_beta.finding_text;
create view api_v1_0_0_beta.finding_text as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, 
          ft.*
    from dissemination_FindingText ft
    left join dissemination_General gen on ft.report_id = gen.report_id
    where gen.is_public=True
;

drop view if exists api_v1_0_0_beta.cap_text;
create view api_v1_0_0_beta.cap_text as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, 
          ct.*
    from dissemination_CAPText ct
    left join dissemination_General gen on ct.report_id = gen.report_id
    where gen.is_public=True
;

drop view if exists api_v1_0_0_beta.note;
create view api_v1_0_0_beta.note as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, 
          note.*
    from dissemination_Note note
    left join dissemination_General gen on note.report_id = gen.report_id
    where gen.is_public=True
;

commit;

notify pgrst,
       'reload schema';

