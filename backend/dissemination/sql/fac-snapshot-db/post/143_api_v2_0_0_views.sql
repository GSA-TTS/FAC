---------------------------------------
-- additional_eins
---------------------------------------
CREATE VIEW api_v2_0_0.additional_eins AS
    SELECT * FROM public_data_v1_0_0.additional_eins ae
    ORDER BY ae.id;

---------------------------------------
-- additional_ueis
---------------------------------------
create view api_v2_0_0.additional_ueis AS
    SELECT * FROM public_data_v1_0_0.additional_ueis au
    ORDER BY au.id;

---------------------------------------
-- corrective_action_plan
---------------------------------------
CREATE VIEW api_v2_0_0.corrective_action_plans AS
    SELECT * FROM public_data_v1_0_0.corrective_action_plans cap
    ORDER BY cap.id;

---------------------------------------
-- finding
---------------------------------------
CREATE VIEW api_v2_0_0.findings as
    SELECT * FROM public_data_v1_0_0.findings f
    ORDER BY f.id;

---------------------------------------
-- finding_text
---------------------------------------
CREATE VIEW api_v2_0_0.findings_text AS
    SELECT * FROM public_data_v1_0_0.findings_text ft
    ORDER BY ft.id;

---------------------------------------
-- federal award
---------------------------------------
CREATE VIEW api_v2_0_0.federal_awards AS
    SELECT * FROM public_data_v1_0_0.federal_awards fa
    ORDER BY fa.id;

---------------------------------------
-- general
---------------------------------------
CREATE VIEW api_v2_0_0.general AS
    SELECT * FROM public_data_v1_0_0.general gen
    ORDER BY gen.id;

---------------------------------------
-- notes_to_sefa
---------------------------------------
CREATE VIEW api_v2_0_0.notes_to_sefa AS
    SELECT * FROM public_data_v1_0_0.notes_to_sefa nts
    ORDER BY nts.id;

---------------------------------------
-- passthrough
---------------------------------------
CREATE VIEW api_v2_0_0.passthrough AS
    SELECT * FROM public_data_v1_0_0.passthrough p
    ORDER BY p.id;

---------------------------------------
-- auditor (secondary auditor)
---------------------------------------
CREATE VIEW api_v2_0_0.secondary_auditors AS
    SELECT * FROM public_data_v1_0_0.secondary_auditors sa
    ORDER BY sa.id;

---------------------------------------
-- combined
---------------------------------------
CREATE VIEW api_v2_0_0.combined AS
    SELECT * FROM public_data_v1_0_0.combined comb
    ORDER BY comb.seq;

---------------------------------------
-- metadata
---------------------------------------
CREATE VIEW api_v2_0_0.metadata AS
    SELECT * FROM public_data_v1_0_0.metadata;

------------------------------------------------------------------------------
-- SUPPRESSED ENDPOINTS
-- These require an API key that has tribal/suppressed data access.
------------------------------------------------------------------------------

---------------------------------------
-- suppressed_corrective_action_plan
---------------------------------------
CREATE VIEW api_v2_0_0.suppressed_corrective_action_plans AS
    SELECT * FROM suppressed_data_v1_0_0.corrective_action_plans cap
    WHERE api_v2_0_0_functions.has_tribal_data_access()
    ORDER BY cap.id;


---------------------------------------
-- suppressed_finding_text
---------------------------------------
CREATE VIEW api_v2_0_0.suppressed_findings_text AS
    SELECT * FROM suppressed_data_v1_0_0.findings_text ft
    WHERE api_v2_0_0_functions.has_tribal_data_access()
    ORDER BY ft.id;

---------------------------------------
-- suppressed_notes_to_sefa
---------------------------------------
CREATE VIEW api_v2_0_0.suppressed_notes_to_sefa AS
    SELECT * FROM suppressed_data_v1_0_0.notes_to_sefa nts
    WHERE api_v2_0_0_functions.has_tribal_data_access()
    ORDER BY nts.id;
