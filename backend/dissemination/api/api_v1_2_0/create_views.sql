begin;
---------------------------------------
-- functions
---------------------------------------
create or replace function cast_text_to_date(the_date varchar)
   returns date
   language sql
   immutable
as
$$
  select to_date(the_date, 'yyyy-mm-dd');
$$;

create or replace function yesnonull(input text)
returns text as $$
begin
  case 
    when input = 'true' then return 'Yes';
    when input = 'false' then return 'No';
    else return null;
  end case;
end;
$$ language plpgsql immutable;

create or replace function yesno(input text)
returns text as $$
begin
  case 
    when input = 'true' then return 'Yes';
    else return 'No';
  end case;
end;
$$ language plpgsql immutable;

create or replace function yesnogsamigration(input text)
returns text as $$
begin
  case 
    when input = 'true' then return 'Yes';
    when input = 'GSA_MIGRATION' then return 'GSA_MIGRATION';
    else return 'No';
  end case;
end;
$$ language plpgsql immutable;

create or replace function yesnogsamigrationnull(input text)
returns text as $$
begin
  case 
    when input = 'true' then return 'Yes';
    when input = 'false' then return 'No';
    when input = 'GSA_MIGRATION' then return 'GSA_MIGRATION';
    else return null;
  end case;
end;
$$ language plpgsql immutable;

create or replace function jsonb_array_to_string(input jsonb)
returns text as $$
begin
  return (
    select string_agg(elem, ',')
    from jsonb_array_elements_text(input) as elem
  );
end;
$$ language plpgsql immutable;
---------------------------------------
-- indexes
---------------------------------------
create index if not exists idx_audit_submission_status on audit_audit (submission_status);
create index if not exists idx_audit_auditee_uei on audit_audit ((audit->'general_information'->>'auditee_uei'));
create index if not exists idx_audit_auditee_email on audit_audit ((audit->'general_information'->>'auditee_email'));
create index if not exists idx_audit_auditor_email on audit_audit ((audit->'general_information'->>'auditor_email'));
create index if not exists idx_audit_fac_accepted_date on audit_audit ((audit->>'fac_accepted_date'));
create index if not exists idx_history_auditor_cert on audit_history (report_id, event, id DESC);
create index if not exists idx_history_auditee_cert on audit_history (report_id, event, id DESC);
create index if not exists idx_audit_date_index ON audit_audit (cast_text_to_date(audit_audit.fac_accepted_date));
---------------------------------------
-- finding_text
---------------------------------------
create view api_v1_2_0.findings_text as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        ft_elem->>'reference_number' as finding_ref_number,
        ft_elem->>'contains_chart_or_table' as contains_chart_or_table,
        ft_elem->>'text_of_finding' as finding_text
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'findings_text') as ft_elem on true
    where
        a.submission_status='disseminated'
        and (a.is_public is true
        or (
            a.is_public is false
            and api_v1_2_0_functions.has_tribal_data_access()
        ))
;
---------------------------------------
-- additional_ueis
---------------------------------------
create view api_v1_2_0.additional_ueis as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        uei_elem as additional_uei
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'additional_ueis') as uei_elem on true
    where
        a.submission_status = 'disseminated'
        and ((a.audit->'general_information'->>'multiple_ueis_covered')::boolean = TRUE)
        and a.audit ? 'additional_ueis'
;
---------------------------------------
-- finding
---------------------------------------
create view api_v1_2_0.findings as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        f_elem->'program'->>'award_reference' as award_reference,
        f_elem->'findings'->>'reference_number' as reference_number,
        f_elem->'material_weakness' as is_material_weakness,
        f_elem->'modified_opinion' as is_modified_opinion,
        f_elem->'other_findings' as is_other_findings,
        f_elem->'other_matters' as is_other_matters,
        f_elem->'findings'->>'prior_references' as prior_finding_ref_numbers,
        f_elem->'questioned_costs' as is_questioned_costs,
        f_elem->'findings'->>'repeat_prior_reference' as is_repeat_finding,
        f_elem->'significant_deficiency' as is_significant_deficiency,
        f_elem->'program'->>'compliance_requirement' as type_requirement
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'findings_uniform_guidance') as f_elem on true
    where
        a.submission_status='disseminated'
;

---------------------------------------
-- federal award
---------------------------------------
create view api_v1_2_0.federal_awards as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        fa_elem->>'award_reference' as award_reference,
        fa_elem->'program'->>'federal_agency_prefix' as federal_agency_prefix,
        fa_elem->'program'->>'three_digit_extension' as federal_award_extension,
        coalesce(fa_elem->'program'->>'additional_award_identification','') as additional_award_identification,
        fa_elem->'program'->>'program_name' as federal_program_name,
        fa_elem->'program'->'amount_expended' as amount_expended,
        fa_elem->'cluster'->>'cluster_name' as cluster_name,
        coalesce(fa_elem->'cluster'->>'other_cluster_name','') as other_cluster_name,
        coalesce(fa_elem->'cluster'->>'state_cluster_name','') as state_cluster_name,
        fa_elem->'cluster'->'cluster_total' as cluster_total,
        fa_elem->'program'->'federal_program_total' as federal_program_total,
        fa_elem->'program'->>'is_major' as is_major,
        fa_elem->'loan_or_loan_guarantee'->>'is_guaranteed' as is_loan,
        coalesce(fa_elem->'loan_or_loan_guarantee'->>'loan_balance_at_audit_period_end','') as loan_balance,
        fa_elem->'direct_or_indirect_award'->>'is_direct' as is_direct,
        coalesce(fa_elem->'program'->>'audit_report_type','') as audit_report_type,
        fa_elem->'program'->'number_of_audit_findings' as findings_count,
        fa_elem->'subrecipients'->>'is_passed' as is_passthrough_award,
        fa_elem->'subrecipients'->'subrecipient_amount' as passthrough_amount
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'federal_awards'->'awards') as fa_elem on true
    where
        a.submission_status='disseminated'
;

---------------------------------------
-- corrective_action_plan
---------------------------------------
create view api_v1_2_0.corrective_action_plans as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        cap_elem->>'reference_number' as finding_ref_number,
        cap_elem->>'contains_chart_or_table' as contains_chart_or_table,
        cap_elem->>'planned_action' as planned_action
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'corrective_action_plan') as cap_elem on true
    where
        a.submission_status='disseminated'
        and (a.is_public is true
        or (
            a.is_public is false
            and api_v1_2_0_functions.has_tribal_data_access()
        ))
;
---------------------------------------
-- notes_to_sefa
---------------------------------------
create view api_v1_2_0.notes_to_sefa as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        coalesce(notes.note->>'note_title','') as title,
        a.audit->'notes_to_sefa'->>'accounting_policies' as accounting_policies,
        a.audit->'notes_to_sefa'->>'is_minimis_rate_used' as is_minimis_rate_used,
        a.audit->'notes_to_sefa'->>'rate_explained' as rate_explained,
        coalesce(notes.note->>'note_content','') as content,
        coalesce(notes.note->>'contains_chart_or_table','') as contains_chart_or_table
    from
        audit_audit as a
	    left join lateral (
	        select jsonb_array_elements(a.audit->'notes_to_sefa'->'notes_to_sefa_entries') as note
	    ) as notes
	    on jsonb_typeof(a.audit->'notes_to_sefa'->'notes_to_sefa_entries') = 'array'
    where
        a.submission_status='disseminated'
        and (a.is_public is true
        or (
            a.is_public is false
            and api_v1_2_0_functions.has_tribal_data_access()
        ))
;
---------------------------------------
-- passthrough
---------------------------------------
create view api_v1_2_0.passthrough as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        fa_elem->>'award_reference' as award_reference,
        pass_elem->>'passthrough_identifying_number' as passthrough_id,
        pass_elem->>'passthrough_name' as passthrough_name
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'federal_awards'->'awards') as fa_elem on true
        join lateral jsonb_array_elements(fa_elem->'direct_or_indirect_award'->'entities') as pass_elem on true
    where
        a.submission_status='disseminated'
;
---------------------------------------
-- general
---------------------------------------
create view api_v1_2_0.general as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        -- auditee
        coalesce(a.audit->'auditee_certification' -> 'auditee_signature' ->> 'auditee_name','') as auditee_certify_name,
        coalesce(a.audit->'auditee_certification' -> 'auditee_signature' ->> 'auditee_title','') as auditee_certify_title,
        a.audit->'general_information'->>'auditee_contact_name' as auditee_contact_name,
        a.audit->'general_information'->>'auditee_email' as auditee_email,
        a.audit->'general_information'->>'auditee_name' as auditee_name,
        a.audit->'general_information'->>'auditee_phone' as auditee_phone,
        a.audit->'general_information'->>'auditee_contact_title' as auditee_contact_title,
        a.audit->'general_information'->>'auditee_address_line_1' as auditee_address_line_1,
        a.audit->'general_information'->>'auditee_city' as auditee_city,
        a.audit->'general_information'->>'auditee_state' as auditee_state,
        a.audit->'general_information'->>'ein' as auditee_ein,
        a.audit->'general_information'->>'auditee_zip' as auditee_zip,
        -- auditor
        coalesce(a.audit->'auditor_certification' -> 'auditor_signature' ->> 'auditor_name','') as auditor_certify_name,
        coalesce(a.audit->'auditor_certification' -> 'auditor_signature' ->> 'auditor_title','') as auditor_certify_title,
        a.audit->'general_information'->>'auditor_phone' as auditor_phone,
        coalesce(a.audit->'general_information'->>'auditor_state','') as auditor_state,
        coalesce(a.audit->'general_information'->>'auditor_city','') as auditor_city,
        a.audit->'general_information'->>'auditor_contact_title' as auditor_contact_title,
        coalesce(a.audit->'general_information'->>'auditor_address_line_1','') as auditor_address_line_1,
        coalesce(a.audit->'general_information'->>'auditor_zip','') as auditor_zip,
        a.audit->'general_information'->>'auditor_country' as auditor_country,
        a.audit->'general_information'->>'auditor_contact_name' as auditor_contact_name,
        a.audit->'general_information'->>'auditor_email' as auditor_email,
        a.audit->'general_information'->>'auditor_firm_name' as auditor_firm_name,
        coalesce(a.audit->'general_information'->>'auditor_international_address', '') as auditor_foreign_address,
        a.audit->'general_information'->>'auditor_ein' as auditor_ein,
        -- agency
        coalesce(a.audit->>'cognizant_agency','') as cognizant_agency,
        coalesce(a.audit->>'oversight_agency','') as oversight_agency,
        -- dates
        to_char(a.created_at AT TIME ZONE 'America/New_York', 'YYYY-MM-DD') as date_created,
        (select to_char(updated_at AT TIME ZONE 'America/New_York', 'YYYY-MM-DD') from public.audit_history h
        where event = 'locked-for-certification'
        and h.report_id = a.report_id
        order by id desc limit 1) as ready_for_certification_date,
        (select to_char(updated_at AT TIME ZONE 'America/New_York', 'YYYY-MM-DD') from public.audit_history h
        where event = 'auditor-certification-completed'
        and h.report_id = a.report_id
        order by id desc limit 1) as auditor_certified_date,        
        (select to_char(updated_at AT TIME ZONE 'America/New_York', 'YYYY-MM-DD') from public.audit_history h
        where event = 'auditee-certification-completed'
        and h.report_id = a.report_id
        order by id desc limit 1) as auditee_certified_date,
        a.fac_accepted_date as submitted_date,
        a.fac_accepted_date,
        a.audit->'general_information'->>'auditee_fiscal_period_end' as fy_end_date,
        a.audit->'general_information'->>'auditee_fiscal_period_start' as fy_start_date,
        a.audit->'general_information'->>'audit_type' as audit_type,
        coalesce(jsonb_array_to_string(a.audit->'audit_information'->'gaap_results'),'') as gaap_results,
        coalesce(jsonb_array_to_string(a.audit->'audit_information'->'sp_framework_basis'),'') as sp_framework_basis,
        coalesce(yesnogsamigrationnull(a.audit->'audit_information'->>'is_sp_framework_required'),'') as is_sp_framework_required,
        coalesce(jsonb_array_to_string(a.audit->'audit_information'->'sp_framework_opinions'),'')as sp_framework_opinions,
        yesnogsamigration(a.audit->'audit_information'->>'is_going_concern_included') as is_going_concern_included,
        yesnogsamigration(a.audit->'audit_information'->>'is_internal_control_deficiency_disclosed') as is_internal_control_deficiency_disclosed,
        yesnogsamigration(a.audit->'audit_information'->>'is_internal_control_material_weakness_disclosed') as is_internal_control_material_weakness_disclosed,
        yesnogsamigration(a.audit->'audit_information'->>'is_material_noncompliance_disclosed') as is_material_noncompliance_disclosed,
        (a.audit->'audit_information'->'dollar_threshold')::bigint  as dollar_threshold,
        yesnogsamigration(a.audit->'audit_information'->>'is_low_risk_auditee') as is_low_risk_auditee,
        coalesce(jsonb_array_to_string(a.audit->'audit_information'->'agencies'),'') as agencies_with_prior_findings,
        a.audit->'general_information'->>'user_provided_organization_type' as entity_type,
        coalesce(a.audit->'general_information'->>'audit_period_other_months','') as number_months,
        coalesce(a.audit->'general_information'->>'audit_period_covered','') as audit_period_covered,
        (a.audit->'federal_awards'->'total_amount_expended')::bigint  as total_amount_expended,
        a.audit ->>'type_audit_code' as type_audit_code,
        a.is_public as is_public,
        a.data_source as data_source,
        yesnogsamigration(a.audit->'audit_information'->>'is_aicpa_audit_guide_included') as is_aicpa_audit_guide_included,
        case 
            when yesno(a.audit->'general_information'->>'multiple_ueis_covered') = 'Yes' 
            and a.audit ? 'additional_ueis'
            then 'Yes'
            else 'No'
        end as is_additional_ueis,
        case 
            when yesno(a.audit->'general_information'->>'multiple_eins_covered') = 'Yes' 
            and a.audit ? 'additional_eins'
            then 'Yes'
            else 'No'
        end as is_multiple_eins,
        case 
            when yesno(a.audit->'general_information'->>'secondary_auditors_exist') = 'Yes' 
            and a.audit ? 'secondary_auditors'
            then 'Yes'
            else 'No'
        end as is_secondary_auditors    
    from
        audit_audit as a
    where 
    	a.submission_status='disseminated'
;
---------------------------------------
-- auditor (secondary auditor)
---------------------------------------
create view api_v1_2_0.secondary_auditors as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        sa_elem->>'secondary_auditor_ein' as auditor_ein,
        sa_elem->>'secondary_auditor_name' as auditor_name,
        sa_elem->>'secondary_auditor_contact_name' as contact_name,
        sa_elem->>'secondary_auditor_contact_title' as contact_title,
        sa_elem->>'secondary_auditor_contact_email' as contact_email,
        sa_elem->>'secondary_auditor_contact_phone' as contact_phone,
        sa_elem->>'secondary_auditor_address_street' as address_street,
        sa_elem->>'secondary_auditor_address_city' as address_city,
        sa_elem->>'secondary_auditor_address_state' as address_state,
        sa_elem->>'secondary_auditor_address_zipcode' as address_zipcode
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'secondary_auditors') as sa_elem on true
    where
        a.submission_status = 'disseminated'
        and ((a.audit->'general_information'->>'secondary_auditors_exist')::boolean = TRUE)
        and a.audit ? 'secondary_auditors'
;
---------------------------------------
-- additional_eins
---------------------------------------
create view api_v1_2_0.additional_eins as
    select
        a.report_id,
        a.audit->'general_information'->>'auditee_uei' as auditee_uei,
        a.audit->>'audit_year' as audit_year,
        ein_elem as additional_ein
    from
        audit_audit as a
        join lateral jsonb_array_elements(a.audit->'additional_eins') as ein_elem on true
    where
        a.submission_status = 'disseminated'
        and ((a.audit->'general_information'->>'multiple_eins_covered')::boolean = TRUE)
        and a.audit ? 'additional_eins'
;
commit;

notify pgrst,
       'reload schema';

