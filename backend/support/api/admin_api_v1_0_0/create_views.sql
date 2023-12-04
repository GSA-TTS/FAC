
begin;


---------------------------------------
-- accesses
---------------------------------------
-- public.audit_access definition

-- Drop table

-- DROP TABLE public.audit_access;

CREATE OR REPLACE VIEW admin_api_v1_0_0.audit_access AS
    SELECT
        aa.role,
        aa.fullname,
        aa.email,
        aa.sac_id,
        aa.user_id
    FROM
        audit_access aa
    WHERE
        admin_api_v1_0_0.has_admin_data_access('SELECT')
    ORDER BY aa.id
;

CREATE OR REPLACE VIEW admin_api_v1_0_0.singleauditchecklist AS
    SELECT
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
        audit_singleauditchecklist sac
    where
        admin_api_v1_0_0.has_admin_data_access('SELECT')
    order by sac.id
;

CREATE OR REPLACE VIEW admin_api_v1_0_0.tribal_access AS
    SELECT
        uup.email,
        up.slug as permission
    FROM
        users_userpermission uup,
        users_permission up
    WHERE
        (uup.permission_id = 1)
        AND (uup.permission_id = up.id)
        AND admin_api_v1_0_0.has_admin_data_access('SELECT')
    ORDER BY uup.id
;

CREATE OR REPLACE VIEW admin_api_v1_0_0.admin_api_events AS
    SELECT
        ae.timestamp,
        ae.api_key_uuid,
        ae.event,
        ae.event_data
    FROM
        support_adminapievent ae
    WHERE
        admin_api_v1_0_0.has_admin_data_access('SELECT')
    ORDER BY ae.id
;


commit;

notify pgrst,
       'reload schema';
