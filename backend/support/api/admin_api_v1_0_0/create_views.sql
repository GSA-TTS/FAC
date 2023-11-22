
begin;


---------------------------------------
-- accesses
---------------------------------------
-- public.audit_access definition

-- Drop table

-- DROP TABLE public.audit_access;

create view admin_api_v1_0_0.audit_access as
    select
        aa.role,
        aa.fullname,
        aa.email,
        aa.sac_id,
        aa.user_id
    from
        audit_access aa
    where
        has_admin_data_access()
        true
    order by aa.id
;

create view admin_api_v1_0_0.singleauditchecklist as
    select
        sac.id,
        sac.date_created,
        sac.submission_status,
        sac.data_source,
        sac.transition_name,
        sac.transition_date,
        sac.report_id,
        sac.audit_type,
        sac.general_information,
        sac.audit_information,
        sac.federal_awards,
        sac.corrective_action_plan,
        sac.findings_text,
        sac.findings_uniform_guidance,
        sac.additional_ueis,
        sac.additional_eins,
        sac.secondary_auditors,
        sac.notes_to_sefa,
        sac.auditor_certification,
        sac.auditee_certification,
        sac.tribal_data_consent,
        sac.cognizant_agency,
        sac.oversight_agency,
        sac.submitted_by_id
    from
        audit_singleauditchecklist as sac
    where
        has_admin_data_access()
    order by sac.id
;

commit;

notify pgrst,
       'reload schema';
