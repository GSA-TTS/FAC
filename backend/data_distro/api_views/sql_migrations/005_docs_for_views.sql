-- run by 0033
begin;

-- adding these as strings since the migrations are a point in time
comment on view api.vw_auditee is 'Information about the entity undergoing the audit';
comment on view api.vw_auditor is 'Information about the Auditing CPA firm conducting the audit';
comment on view api.vw_cap_text is 'Corrective action plan text';
comment on view api.vw_federal_award is 'Information about the federal award section of the form';
comment on view api.vw_findings is 'A finding from the audit';
comment on view api.vw_findings_text is 'Specific findings details';
comment on view api.vw_general is 'Data from the General Info and Audit Info forms with links to other parts of the form';
comment on view api.vw_note is 'Note to Schedule of Expenditures of Federal Awards (SEFA)';
comment on view api.vw_passthrough is 'The pass-through entity information, when it is not a direct federal award';
comment on view api.vw_revision is 'Documents what was revised on the associated form from the previous version';

commit;
