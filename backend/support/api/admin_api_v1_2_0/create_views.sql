
begin;


---------------------------------------
-- accesses
---------------------------------------
-- public.audit_access definition

-- Drop table

-- DROP TABLE public.audit_access;

CREATE OR REPLACE VIEW admin_api_v1_2_0.audit_access AS
    SELECT
        aa.role,
        aa.fullname,
        aa.email,
        aa.audit_id,
        aa.user_id
    FROM
        public.audit_access aa
    WHERE
        admin_api_v1_2_0_functions.has_admin_data_access('READ')
    ORDER BY aa.id
;

CREATE OR REPLACE VIEW admin_api_v1_2_0.audit AS
    SELECT
        audit.id,
        audit.created_at as date_created,
        audit.submission_status,
        audit.data_source,
        audit.report_id,
        audit.audit_type,
        audit.audit->'general_information' as general_information,
        audit.audit->'audit_information' as audit_information,
        audit.audit->'federal_awards' as federal_awards,
        audit.audit->'corrective_action_plan' as corrective_action_plan,
        audit.audit->'findings_text' as findings_text,
        audit.audit->'findings_uniform_guidance' as findings_uniform_guidance,
        audit.additional_ueis as additional_ueis,
        audit.additional_eins as additional_eins,
        audit.audit->'secondary_auditors' as secondary_auditors,
        audit.audit->'notes_to_sefa' as notes_to_sefa,
        audit.audit->'auditor_certification' as auditor_certification,
        audit.audit->'auditee_certification' as auditee_certification,
        audit.audit->'tribal_data_consent' as tribal_data_consent,
        audit.cognizant_agency,
        audit.oversight_agency,
        audit.created_by_id
    from
        public.audit_audit audit
    where
        admin_api_v1_2_0_functions.has_admin_data_access('READ')
    order by audit.id
;

CREATE OR REPLACE VIEW admin_api_v1_2_0.tribal_access AS
    SELECT
        uup.email,
        up.slug as permission
    FROM
        users_userpermission uup,
        users_permission up
    WHERE
        (uup.permission_id = up.id)
        AND (up.slug = 'read-tribal')
        AND admin_api_v1_2_0_functions.has_admin_data_access('READ')
    ORDER BY uup.id
;

CREATE OR REPLACE VIEW admin_api_v1_2_0.admin_api_events AS
    SELECT
        ae.timestamp,
        ae.api_key_uuid,
        ae.event,
        ae.event_data
    FROM
        public.support_adminapievent ae
    WHERE
        admin_api_v1_2_0_functions.has_admin_data_access('READ')
    ORDER BY ae.id
;


commit;

notify pgrst,
       'reload schema';
