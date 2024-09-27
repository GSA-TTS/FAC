select count(report_id) from dissemination_general where api_v1_1_0.batch(id) = 2;

grant select on dissemination_general to api_fac_gov;


alter default privileges
    in schema api_v1_1_0_functions
    grant select
-- this includes views
on tables
to api_fac_gov;

SET SESSION SESSION AUTHORIZATION api_fac_gov;

SELECT SESSION_USER, CURRENT_USER;
SET SESSION SESSION AUTHORIZATION 'api_fac_gov';
SELECT SESSION_USER, CURRENT_USER;
RESET SESSION AUTHORIZATION;
SELECT SESSION_USER, CURRENT_USER;

SET SESSION SESSION AUTHORIZATION 'api_fac_gov';
select count(report_id) from dissemination_general where api_v1_1_0.batch(id) = 2;

GRANT SELECT ON public.dissemination_general to api_fac_gov;
GRANT SELECT ON public.dissemination_federalaward to api_fac_gov;

REVOKE SELECT ON public.dissemination_federalaward from api_fac_gov;
REVOKE SELECT ON public.dissemination_general from api_fac_gov;

SET SESSION SESSION AUTHORIZATION 'api_fac_gov';
select api_v1_1_0.get_federal_award_batch(2);


-------------------

SELECT id, report_id FROM public.dissemination_general WHERE id < 3000;
