-- uniting findings and findings text
-- may want to add auditee name, agency, fed program name, cap text and cpa name

-- TODO fix seqence_number spelling

create view vw_findings as
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
