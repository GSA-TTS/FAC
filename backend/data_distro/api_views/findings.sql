-- uniting findings and findings text
-- may want to add auditee name, agency, fed program name, cap text and cpa name

-- TODO fix seqence_number spelling

-- Findings with list of associated findings text records
create or replace view view vw_findings as
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
)
select findings.*, findings_text.findings_text_id
from findings
left join findings_text on findings.id=findings_text.finding_id
;

grant select on vw_findings to anon;

-- Findings text
create or replace view vw_findings_text as
 select * from data_distro_findingtext
 where data_distro_findingtext.is_public=True
;

grant select on vw_findings_text to anon;
