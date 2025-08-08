update audit_singleauditchecklist
set tribal_data_consent = '{"is_tribal_information_authorized_to_be_public": false, "tribal_authorization_certifying_official_name": "Fake Randomized Name", "tribal_authorization_certifying_official_title": "Fake Randomized Title"}'
where report_id in (
	SELECT report_id FROM audit_singleauditchecklist
	TABLESAMPLE BERNOULLI(70)
	where general_information->>'auditee_fiscal_period_end' like '%2019%'
	limit 100
);

update audit_singleauditchecklist
set tribal_data_consent = '{"is_tribal_information_authorized_to_be_public": false, "tribal_authorization_certifying_official_name": "Fake Randomized Name", "tribal_authorization_certifying_official_title": "Fake Randomized Title"}'
where report_id in (
	SELECT report_id FROM audit_singleauditchecklist
	TABLESAMPLE BERNOULLI(70)
	where general_information->>'auditee_fiscal_period_end' like '%2020%'
	limit 100
);

update audit_singleauditchecklist
set tribal_data_consent = '{"is_tribal_information_authorized_to_be_public": false, "tribal_authorization_certifying_official_name": "Fake Randomized Name", "tribal_authorization_certifying_official_title": "Fake Randomized Title"}'
where report_id in (
	SELECT report_id FROM audit_singleauditchecklist
	TABLESAMPLE BERNOULLI(70)
	where general_information->>'auditee_fiscal_period_end' like '%2021%'
	limit 100
);

update audit_singleauditchecklist
set tribal_data_consent = '{"is_tribal_information_authorized_to_be_public": false, "tribal_authorization_certifying_official_name": "Fake Randomized Name", "tribal_authorization_certifying_official_title": "Fake Randomized Title"}'
where report_id in (
	SELECT report_id FROM audit_singleauditchecklist
	TABLESAMPLE BERNOULLI(70)
	where general_information->>'auditee_fiscal_period_end' like '%2022%'
	limit 100
);

update audit_singleauditchecklist
set tribal_data_consent = '{"is_tribal_information_authorized_to_be_public": false, "tribal_authorization_certifying_official_name": "Fake Randomized Name", "tribal_authorization_certifying_official_title": "Fake Randomized Title"}'
where report_id in (
	SELECT report_id FROM audit_singleauditchecklist
	TABLESAMPLE BERNOULLI(70)
	where general_information->>'auditee_fiscal_period_end' like '%2023%'
	limit 100
);
