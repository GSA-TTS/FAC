update dissemination_general
set 
  resubmission_status = 'original_submission',
  resubmission_version = 1
where report_id in (
	SELECT report_id FROM dissemination_general
	TABLESAMPLE BERNOULLI(100)
	where audit_year like '%2019%'
	limit 100
);

update dissemination_general
set 
  resubmission_status = 'most_recent',
  resubmission_version = floor(random() * 10) + 2
where report_id in (
	SELECT report_id FROM dissemination_general
	TABLESAMPLE BERNOULLI(100)
	where audit_year like '%2020%'
	limit 100
);

update dissemination_general
set 
  resubmission_status = 'deprecated_via_resubmission',
  resubmission_version = floor(random() * 10) + 2
where report_id in (
	SELECT report_id FROM dissemination_general
	TABLESAMPLE BERNOULLI(100)
	where audit_year like '%2021%'
	limit 100
);
