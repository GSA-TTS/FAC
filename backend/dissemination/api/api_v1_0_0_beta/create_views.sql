
begin;

create table api_v1_0_0_beta.metadata as
select * 
from 
    (values 	('version', '1.0.0-beta'), 
            	('last_updated', '2023-07-14'))
as metadata(key, value)
;

create view api_v1_0_0_beta.general as
    select gen.*, 
          award.federal_agency_prefix, award.federal_award_extension
    from dissemination_General gen
    left outer join dissemination_FederalAward award on gen.report_id = award.report_id
    where gen.is_public=true 
    -- MCJ When it comes time to enable tribal access, this is what it looks like.
    -- For each view, we add a conditional clause where the data is not public and 
    -- the user also has tribal access based on headers from api.data.gov.
    -- or (gen.is_public=false and has_tribal_data_access())
;

create view api_v1_0_0_beta.auditor as
    select gen.auditee_uei, gen.auditee_ein, gen.audit_year,
           sa.*
    from dissemination_SecondaryAuditor sa
    left join dissemination_General gen on sa.report_id = gen.report_id
    where gen.is_public=True
;

create view api_v1_0_0_beta.federal_award as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, award.*
    from dissemination_FederalAward award
    left join dissemination_General gen on award.report_id = gen.report_id
    where gen.is_public=True
;

create view api_v1_0_0_beta.finding as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, 
          award.federal_agency_prefix, award.federal_award_extension, 
          finding.*
    from dissemination_Finding finding
    left join dissemination_FederalAward award 
        on award.report_id = finding.report_id 
          and award.award_reference = finding.award_reference
    left join dissemination_General gen on award.report_id = gen.report_id
    where gen.is_public=True
;

create view api_v1_0_0_beta.finding_text as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, 
          ft.*
    from dissemination_FindingText ft
    left join dissemination_General gen on ft.report_id = gen.report_id
    where gen.is_public=True
;

create view api_v1_0_0_beta.cap_text as
    select gen.auditee_uei, gen.auditee_ein, gen.fy_start_date, gen.fy_end_date, gen.audit_year, 
          ct.*
    from dissemination_CAPText ct
    left join dissemination_General gen on ct.report_id = gen.report_id
    where gen.is_public=True
;

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

