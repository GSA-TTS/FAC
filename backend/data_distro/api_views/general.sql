-- Current script to recreate views
-- Run create docs to update view comment
-- Takes the General model and adds Auditor and Auditee information for easy searching
-- (Possible improvements: add Federal Program Name from Federal Award)

begin;

drop view if exists api.vw_general;
create view api.vw_general as
with gen as (
    select *
    from data_distro_general
    where data_distro_general.is_public=True
),
auditee as (
    select auditee_name, id
    from data_distro_auditee
),
auditor as (
    select cpa_firm_name, id
    from data_distro_auditor
),
secondary_auditor as (
    select distinct general_id, array_agg(auditor_id) as secondary_auditor_id
    from data_distro_general_secondary_auditors
    group by general_id
),
federal_award as (
    select distinct general_id, array_agg(federalaward_id) as federal_award_id
    from data_distro_general_federal_awards
    group by general_id
),
findings as (
    select distinct general_id, array_agg(finding_id) as finding_id
    from data_distro_general_findings
    group by general_id
),
findings_text as (
  select general_id, array_agg(findingtext_id) as finding_text_id
  from data_distro_general_findings_text
  group by general_id
),
notes as (
    select distinct general_id, array_agg(note_id) as note_id
    from data_distro_general_notes
    group by general_id
),
cap_text as (
    select distinct general_id, array_agg(captext_id) as cap_text_id
    from data_distro_general_cap_text
    group by general_id
),
passthrough as (
    select distinct general_id, array_agg(passthrough_id) as passthrough_id
    from data_distro_general_passthrough
    group by general_id
)
select gen.*, auditee.auditee_name, auditor.cpa_firm_name, secondary_auditor.secondary_auditor_id,
    federal_award.federal_award_id, findings.finding_id, findings_text.finding_text_id, notes.note_id,
    cap_text.cap_text_id, passthrough.passthrough_id
from gen
left join auditee on auditee.id=gen.auditee_id
left join auditor on auditor.id=gen.primary_auditor_id
left join secondary_auditor on secondary_auditor.general_id=gen.id
left join federal_award on federal_award.general_id=gen.id
left join findings on findings.general_id=gen.id
left join findings_text on findings_text.general_id=gen.id
left join notes on notes.general_id=gen.id
left join cap_text on cap_text.general_id=gen.id
left join passthrough on passthrough.general_id=gen.id
;

commit;

notify pgrst,
       'reload schema';

