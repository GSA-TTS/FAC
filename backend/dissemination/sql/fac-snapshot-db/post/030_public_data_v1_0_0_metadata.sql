CREATE OR REPLACE FUNCTION public_data_v1_0_0.create_metadata()
  RETURNS VOID
AS
$ct$
BEGIN
  CREATE TABLE public_data_v1_0_0.metadata AS
    SELECT 'additional_eins' 
      AS table, COUNT(*)
      FROM public_data_v1_0_0.additional_eins
    UNION
    SELECT 'additional_ueis' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.additional_ueis
    UNION
    SELECT 'combined' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.combined
    UNION
    SELECT 'federal_awards' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.federal_awards
    UNION
    SELECT 'findings_text' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.findings_text
    UNION
    SELECT 'findings' 
      AS table, COUNT(*)
      FROM public_data_v1_0_0.findings
    UNION
    SELECT 'general' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.general
    UNION
    SELECT 'notes_to_sefa' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.notes_to_sefa
    UNION
    SELECT 'passthrough' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.passthrough
    UNION
    SELECT 'secondary_auditors' 
      AS table, COUNT(*) 
      FROM public_data_v1_0_0.secondary_auditors
    UNION
    SELECT 'suppressed_corrective_action_plans' 
      AS table, COUNT(*) 
      FROM suppressed_data_v1_0_0.corrective_action_plans
    UNION
    SELECT 'suppressed_findings_text' 
      AS table, COUNT(*)
      FROM suppressed_data_v1_0_0.findings_text
    UNION
    SELECT 'suppressed_notes_to_sefa' 
      AS table, COUNT(*) 
      FROM suppressed_data_v1_0_0.notes_to_sefa
    UNION
    SELECT 'public_submission_count'
      AS table, COUNT(*)
      FROM public_data_v1_0_0.general gen
      WHERE gen.is_public = true
    UNION
    SELECT 'suppressed_submission_count'
      AS table, COUNT(*)
      FROM public_data_v1_0_0.general gen
      WHERE gen.is_public = false
    ;
END
$ct$
LANGUAGE plpgsql;

DO LANGUAGE plpgsql
$GO$
  BEGIN
    RAISE info 'Creating metadata table';
    PERFORM public_data_v1_0_0.create_metadata();
  END
$GO$;
