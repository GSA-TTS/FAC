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
drop view if exists  api.vw_findings_text_singleauditchecklist;
create view api.vw_findings_text_singleauditchecklist AS 
select
    id,
    -- 20230601 HDMS FIXME: Bellow is the list of missing fields from the original view
    -- sequence_number,
    -- dbkey,
    -- audit_year,
    -- is_public,
    -- general_id,
    (jsonb_array_elements(findings_text->'FindingsText'->'findings_text_entries')->>'text_of_finding') as text,
    (jsonb_array_elements(findings_text->'FindingsText'->'findings_text_entries')->>'reference_number') as finding_ref_number,
    (jsonb_array_elements(findings_text->'FindingsText'->'findings_text_entries')->>'contains_chart_or_table') as charts_tables
from audit_singleauditchecklist;

-- drop view if exists api.vw_unified_findings_text;
-- create view api.vw_unified_findings_text as
-- select * from api.vw_findings_text
-- union all
-- select * from api.vw_findings_text_singleauditchecklist
-- ;

commit;

notify pgrst,
       'reload schema';

