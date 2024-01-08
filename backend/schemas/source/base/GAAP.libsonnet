local audit_info_data = import '../audit/audit-info-values.json';

{
  gaap_results: audit_info_data.gaap_results,
  sp_framework_basis: audit_info_data.sp_framework_basis,
  sp_framework_opinions: audit_info_data.sp_framework_opinions,
}
