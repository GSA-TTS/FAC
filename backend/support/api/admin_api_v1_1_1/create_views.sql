
begin;


---------------------------------------
-- accesses
---------------------------------------
-- public.audit_access definition

-- Drop table

-- DROP TABLE public.audit_access;

CREATE OR REPLACE VIEW admin_api_v1_1_1.audit_access AS
    SELECT
        aa.role,
        aa.fullname,
        aa.email,
        aa.sac_id,
        aa.user_id
    FROM
        public.audit_access aa
    WHERE
        admin_api_v1_1_1_functions.has_admin_data_access('READ')
    ORDER BY aa.id
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.singleauditchecklist AS
    SELECT
        audit.*
    from
        public.audit_audit audit
    where
        admin_api_v1_1_1_functions.has_admin_data_access('READ')
    order by audit.id
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.tribal_access AS
    SELECT
        uup.email,
        up.slug as permission
    FROM
        users_userpermission uup,
        users_permission up
    WHERE
        (uup.permission_id = up.id)
        AND (up.slug = 'read-tribal')
        AND admin_api_v1_1_1_functions.has_admin_data_access('READ')
    ORDER BY uup.id
;

CREATE OR REPLACE VIEW admin_api_v1_1_1.admin_api_events AS
    SELECT
        ae.timestamp,
        ae.api_key_uuid,
        ae.event,
        ae.event_data
    FROM
        public.support_adminapievent ae
    WHERE
        admin_api_v1_1_1_functions.has_admin_data_access('READ')
    ORDER BY ae.id
;


commit;

notify pgrst,
       'reload schema';
