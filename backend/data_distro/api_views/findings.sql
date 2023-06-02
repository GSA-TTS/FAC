-- Current script to recreate views
-- Run create docs to update view comment
-- Uniting findings and findings text
-- (May want to add auditee name, agency, fed program name, cap text and cpa name)

begin;

-- Findings with list of associated findings text records
drop view if exists api.vw_findings;
create view api.vw_findings as
with findings as (
    select *
    from data_distro_finding
    where data_distro_finding.is_public=True
),
findings_text as (
    select distinct finding_id,
        array_agg(findingtext_id) as findings_text_id
    from data_distro_finding_findings_text
    group by finding_id
),
gen as (
    select finding_id, array_agg(general_id) as general_id
    from data_distro_general_findings
    group by finding_id
)
select findings.*, findings_text.findings_text_id, gen.general_id
from findings
left join findings_text on findings.id=findings_text.finding_id
left join gen on findings.id=gen.finding_id
;

-- Revised findings with list of associated findings text records
drop view if exists api.vw_revised_findings;
create view api.vw_revised_findings as
select
  -- 20230602 HDMS FIXME: Below is the list of missing fields from the original view
  -- id,
  -- audit_id,
  -- audit_findings_id,
  -- dbkey,
  -- is_public,
  -- findings_text_id,
  -- general_id,
  (e.value->>'modified_opinion')::boolean as modified_opinion,
  (e.value->>'other_matters')::boolean as other_non_compliance,
  (e.value->>'material_weakness')::boolean as material_weakness,
  (e.value->>'significant_deficiency')::boolean as significant_deficiency,
  (e.value->>'other_findings')::boolean as other_findings,        
  (e.value->>'questioned_costs')::boolean as questioned_costs,
  (e.value->'findings'->>'repeat_prior_reference')::boolean as repeat_finding,
  (e.value->'findings'->>'reference_number') as finding_ref_number,  
  (e.value->'findings'->>'prior_references') as prior_finding_ref_numbers,
  (e.value->'program'->>'compliance_requirement') as type_requirement,
  substring(general_information ->> 'auditee_fiscal_period_start',1,4) as audit_year
from 
  audit_singleauditchecklist a
cross join lateral 
  jsonb_array_elements(a.findings_uniform_guidance->'FindingsUniformGuidance'->'findings_uniform_guidance_entries') e
;

-- 20230602 HDMS FIXME: Uncomment unified view below once the above view is fixed
-- drop view if exists api.vw_unified_findings;
-- create view api.vw_unified_findings as
-- select * from api.vw_findings
-- union all
-- select * from api.vw_revised_findings
-- ;


-- Findings text
drop view if exists api.vw_findings_text;
create view api.vw_findings_text as
with findings_text as (
 select *
 from data_distro_findingtext
 where data_distro_findingtext.is_public=True
),
gen as (
  select findingtext_id, array_agg(general_id) as general_id
  from data_distro_general_findings_text
  group by findingtext_id
)
select findings_text.*, gen.general_id
from findings_text
left join gen on gen.findingtext_id=findings_text.id
;

-- Findings text singleauditchecklist
drop view if exists  api.vw_revised_findings_text;
create view api.vw_revised_findings_text as 
select
    -- 20230601 HDMS FIXME: Below is the list of missing fields from the original view
    -- id,
    -- sequence_number,
    -- dbkey,
    -- is_public,
    -- general_id,
    substring(a.general_information ->> 'auditee_fiscal_period_start',1,4) as audit_year,
    (e.value->>'text_of_finding') as text,
    (e.value->>'reference_number') as finding_ref_number,
    (e.value->>'contains_chart_or_table') as charts_tables
from 
  audit_singleauditchecklist a
cross join lateral 
  jsonb_array_elements(a.findings_text->'FindingsText'->'findings_text_entries') e ;

-- 20230602 HDMS FIXME: Uncomment unified view below once the above view is fixed
-- drop view if exists api.vw_unified_findings_text;
-- create view api.vw_unified_findings_text as
-- select * from api.vw_findings_text
-- union all
-- select * from api.vw_revised_findings_text
-- ;

commit;

notify pgrst,
       'reload schema';

