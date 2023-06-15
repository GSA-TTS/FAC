"""
Using the OpenAPI structure to add docs for data
The field name is going to be a short name, the long name is going to be a short explanation and the description is going to be for the data source.

This is where the model docs descriptions come from. Keep formatting consistent so we can automatically create upload mappings and documentation.

These strings are formatted:
"Data sources: <form with year>: <line number>; <form with year>: <line number> Census mapping: <table name as it appears on the Data Key>, <field name from download>"

If more than one table populates that field:
"Data sources: <form with year>: <line number>; <form with year>: <line number> Census mapping: <table name as it appears on the Data Key>, <field name from download> (AND) Data sources: <form with year>: <line number>; <form with year>: <line number> Census mapping: <table name as it appears on the Data Key>, <field name from download>"

"""

""" Narrative API documentation. """
API_DESCRIPTION = """Data from the Federal Audit Clearinghouse"""


""" Model choices """
# These have not been implemented yet, we will see if the data allows for it

# TYPEREPORT_FS
# TYPEREPORT_SP_FRAMEWORK
# TYPEREPORT_MP
type_reports_choices = [
    ("U", "Unqualifed"),
    ("Q", "Qualified"),
    ("A", "Adverse"),
    ("D", "Disclaimer"),
]

# SP_FRAMEWORK
sp_framework_choices = [
    ("Cash basis", "Cash basis"),
    ("Tax basis", "Tax basis"),
    ("Regulatory basis", "Regulatory basis"),
    ("Contractual basis", "Contractual basis"),
    ("Other basis", "Other basis"),
]

# TYPEREQUIREMENT
type_requirement_choices = [
    ("A", "Activities allowed or unallowed"),
    ("B", "Allowable costs/cost principles"),
    ("C", "Cash management"),
    ("D", "Davis-Bacon Act"),
    ("E", "Eligibility"),
    ("F", "Equipment and real property management"),
    ("G", "Matching, level of effort, earmarking"),
    ("H", "Period of availability of Federal funds"),
    ("I", "Procurement and suspension and debarment"),
    ("J", "Program income"),
    ("K", "Real property acquisition and relocation assistance"),
    ("L", "Reporting"),
    ("M", "Subrecipient monitoring"),
    ("N", "Special tests and provisions"),
    ("O", "None"),
    ("P", "Other"),
]

# OVERSIGHTAGENCY.
cognizant_agency_over_choices = [
    ("C", "Cognizant agency"),
    ("O", "Oversight agency"),
]

# TYPE_ID
type_id_choices = [
    ("1", "Accounting Standards"),
    ("2", "10% Rule"),
    ("3", "Additional"),
    ("4", "Special"),
]


"""
Advanced explanation docs

These have special formatting so we can map data models to the public downloads. That makes uploading data easier.
"""

# check data source
agency_prior_findings = "Data sources: SF-SAC 1997-2000: III/5; SF-SAC 2001-2003: III/9; SF-SAC 2004-2007: III/8; SF-SAC 2008-2009: III/8; SF-SAC 2010-2012: III/8; SF-SAC 2013-2015: III/5; SF-SAC 2016-2018: III/3/d; SF-SAC 2019-2021: III/3/d; SF-SAC 2022: III/3/d Census mapping: AGENCIES, AGENCY"
agency_cfda = "Data sources: SF-SAC 1997-2000: III/5; SF-SAC 2001-2003: III/9; SF-SAC 2004-2007: III/8; SF-SAC 2008-2009: III/8; SF-SAC 2010-2012: III/8; SF-SAC 2013-2015: III/5; SF-SAC 2016-2018: III/3/d; SF-SAC 2019-2021: III/3/d; SF-SAC 2022: III/3/d Census mapping: AGENCIES, AGENCYCFDA"
audit_year_captext = "Census mapping: CAPTEXT, AUDITYEAR"
audit_year_cfdainfo = "Census mapping: CFDA INFO, AUDITYEAR"
audit_year_findings = "Census mapping: FINDINGS, AUDITYEAR"
audit_year_findingstext = "Census mapping: FINDINGSTEXT, AUDITYEAR"
audit_year_general = "Census mapping: GENERAL, AUDITYEAR"
audit_year_notes = "Census mapping: NOTES, AUDITYEAR"
audit_year_passthrough = "Census mapping: PASSTHROUGH, AUDITYEAR"
audit_year_revisions = "Census mapping: REVISIONS, AUDITYEAR"
dbkey_captext = "Census mapping: CAPTEXT, DBKEY"
dbkey_cfdainfo = "Census mapping: CFDA INFO, DBKEY"
dbkey_findings = "Census mapping: FINDINGS, DBKEY"
dbkey_findingstext = "Census mapping: FINDINGSTEXT, DBKEY"
dbkey_general = "Census mapping: GENERAL, DBKEY"
dbkey_notes = "Census mapping: NOTES, DBKEY"
dbkey_passthrough = "Census mapping: PASSTHROUGH, DBKEY"
dbkey_revisions = "Census mapping: REVISIONS, DBKEY"

ein_list = "Data sources: SF-SAC 1997-2000: I/5/a; SF-SAC 2001-2003: I/5/a; SF-SAC 2004-2007: I/5/a; SF-SAC 2008-2009: I/4/a; SF-SAC 2010-2012: I/4/a; SF-SAC 2013-2015: I/4/a; SF-SAC 2016-2018: I/4/a; SF-SAC 2019-2021: I/4/a; SF-SAC 2022: I/4/a Census mapping: GENERAL, EIN (AND) Data sources: SF-SAC 2001-2003: I/5/c; SF-SAC 2004-2007: I/5/c; SF-SAC 2008-2009: I/4/c; SF-SAC 2010-2012: I/4/c; SF-SAC 2013-2015: I/4/c; SF-SAC 2016-2018: I/4/c; SF-SAC 2019-2021: I/4/c; SF-SAC 2022: I/4/c Census mapping: EIN INFO, EIN"
charts_tables_captext = "Census mapping: CAPTEXT, CHARTSTABLES"
charts_tables_findingstext = "Census mapping: FINDINGSTEXT, CHARTSTABLES"
finding_ref_nums_captext = "Data sources: SF-SAC 2019-2021: IV/1; SF-SAC 2022: IV/1 Census mapping: CAPTEXT, FINDINGREFNUMS"
finding_ref_nums_cfdainfo = "Data sources: SF-SAC 1997-2000: III/7/e; SF-SAC 2001-2003: III/11/b; SF-SAC 2004-2007: III/10/b; SF-SAC 2008-2009: III/10/b; SF-SAC 2010-2012: III/10/b; SF-SAC 2013-2015: III/7/d; SF-SAC 2016-2018: III/4/e; SF-SAC 2019-2021: III/4/e; SF-SAC 2022: III/4/e Census mapping: CFDA INFO, FINDINGREFNUMS"
finding_ref_nums_findings = "Data sources: SF-SAC 2013-2015: III/7/d; SF-SAC 2016-2018: III/4/e; SF-SAC 2019-2021: III/4/e; SF-SAC 2022: III/4/e Census mapping: FINDINGS, FINDINGSREFNUMS"
finding_ref_nums_findingstext = "Data sources: SF-SAC 2019-2021: III/5/a; SF-SAC 2022: III/5/a Census mapping: FINDINGSTEXT, FINDINGREFNUMS"
seq_number_captext = "Census mapping: CAPTEXT, SEQ_NUMBER"
seq_number_findingstext = "Census mapping: FINDINGSTEXT, SEQ_NUMBER"
seq_number_notes = "Census mapping: NOTES, SEQ_NUMBER"
text_captext = "Data sources: SF-SAC 2019-2021: IV/2; SF-SAC 2022: IV/2 Census mapping: CAPTEXT, TEXT"
text_findingstext = "Data sources: SF-SAC 2019-2021: III/5/b; SF-SAC 2022: III/5/b Census mapping: FINDINGSTEXT, TEXT"
amount = "Data sources: SF-SAC 1997-2000: III/6/c; SF-SAC 2001-2003: III/10/d; SF-SAC 2004-2007: III/9/e; SF-SAC 2008-2009: III/9/e; SF-SAC 2010-2012: III/9/f; SF-SAC 2013-2015: III/6/d; SF-SAC 2016-2018: II/1/e; SF-SAC 2019-2021: II/1/e; SF-SAC 2022: II/1/e Census mapping: CFDA INFO, AMOUNT"
arra = "Data sources: SF-SAC 2010-2012: III/9/d; SF-SAC 2013-2015: III/6/g Census mapping: CFDA INFO, ARRA"
award_identification = "Data sources: SF-SAC 2016-2018: II/1/c; SF-SAC 2019-2021: II/1/c; SF-SAC 2022: II/1/c Census mapping: CFDA INFO, AWARDIDENTIFICATION"
cfda = "Data sources: SF-SAC 1997-2000: III/6/a; SF-SAC 2001-2003: III/10/a; SF-SAC 2004-2007: III/9/a & III/9/b combined; SF-SAC 2008-2009: III/9/a & III/9/b combined; SF-SAC 2010-2012: III/9/a & III/9/b combined; SF-SAC 2013-2015: III/6/a & III/6/b combined; SF-SAC 2016-2018: II/1/a & II/1/b combined; SF-SAC 2019-2021: II/1/a & II/1/b combined; SF-SAC 2022: II/1/a & II/1/b combined Census mapping: CFDA INFO, CFDA"
cfda_program_name = "Census mapping: CFDA INFO, CFDAPROGRAMNAME"
cluster_name = "Data sources: SF-SAC 2016-2018: II/1/f; SF-SAC 2019-2021: II/1/f; SF-SAC 2022: II/1/f Census mapping: CFDA INFO, CLUSTERNAME"
cluster_total = "Data sources: SF-SAC 2016-2018: II/1/h; SF-SAC 2019-2021: II/1/h; SF-SAC 2022: II/1/h Census mapping: CFDA INFO, CLUSTERTOTAL"
direct = "Data sources: SF-SAC 2001-2003: III/10/e; SF-SAC 2004-2007: III/9/f; SF-SAC 2008-2009: III/9/f; SF-SAC 2010-2012: III/9/g; SF-SAC 2013-2015: III/6/h; SF-SAC 2016-2018: II/1/k; SF-SAC 2019-2021: II/1/k; SF-SAC 2022: II/1/k Census mapping: CFDA INFO, DIRECT"
elec_audits_id_cfdainfo = "Census mapping: CFDA INFO, ELECAUDITSID"
elec_audits_id_findings = "Census mapping: FINDINGS, ELECAUDITSID"
elec_audits_id_passthrough = "Census mapping: PASSTHROUGH, ELECAUDITSID"
federal_program_name = "Data sources: SF-SAC 1997-2000: III/6/b; SF-SAC 2001-2003: III/10/c; SF-SAC 2004-2007: III/9/d; SF-SAC 2008-2009: III/9/d; SF-SAC 2010-2012: III/9/e; SF-SAC 2013-2015: III/6/c; SF-SAC 2016-2018: II/1/d; SF-SAC 2019-2021: II/1/d; SF-SAC 2022: II/1/d Census mapping: CFDA INFO, FEDERALPROGRAMNAME"
findings_count = "Data sources: SF-SAC 2013-2015: III/6/k; SF-SAC 2016-2018: III/1/c; SF-SAC 2019-2021: III/1/c; SF-SAC 2022: III/1/c Census mapping: CFDA INFO, FINDINGSCOUNT"
loan_balance = "Data sources: SF-SAC 2016-2018: II/1/j; SF-SAC 2019-2021: II/1/j; SF-SAC 2022: II/1/j Census mapping: CFDA INFO, LOANBALANCE"
loans = "Data sources: SF-SAC 2013-2015: III/6/f; SF-SAC 2016-2018: II/1/i; SF-SAC 2019-2021: II/1/i; SF-SAC 2022: II/1/i Census mapping: CFDA INFO, LOANS"
major_program = "Data sources: SF-SAC 1997-2000: III/7/a; SF-SAC 2001-2003: III/10/f; SF-SAC 2004-2007: III/9/g; SF-SAC 2008-2009: III/9/g; SF-SAC 2010-2012: III/9/h; SF-SAC 2013-2015: III/6/i; SF-SAC 2016-2018: III/1/a; SF-SAC 2019-2021: III/1/a; SF-SAC 2022: III/1/a Census mapping: CFDA INFO, MAJORPROGRAM"
other_cluster_name = "Census mapping: CFDA INFO, OTHERCLUSTERNAME"
passthrough_amount = "Data sources: SF-SAC 2016-2018: II/1/o; SF-SAC 2019-2021: II/1/o; SF-SAC 2022: II/1/o Census mapping: CFDA INFO, PASSTHROUGHAMOUNT"
passthrough_award = "Data sources: SF-SAC 2016-2018: II/1/n; SF-SAC 2019-2021: II/1/n; SF-SAC 2022: II/1/n Census mapping: CFDA INFO, PASSTHROUGHAWARD"
program_total = "Data sources: SF-SAC 2016-2018: II/1/g; SF-SAC 2019-2021: II/1/g; SF-SAC 2022: II/1/g Census mapping: CFDA INFO, PROGRAMTOTAL"
research_and_development = "Data sources: SF-SAC 2001-2003: III/10/b; SF-SAC 2004-2007: III/9/c; SF-SAC 2008-2009: III/9/c; SF-SAC 2010-2012: III/9/c; SF-SAC 2013-2015: III/6/e Census mapping: CFDA INFO, RD"
state_cluster_name = "Census mapping: CFDA INFO, STATECLUSTERNAME"
type_report_major_program_cfdainfo = "Data sources: SF-SAC 2004-2007: III/9/h; SF-SAC 2008-2009: III/9/h; SF-SAC 2010-2012: III/9/i; SF-SAC 2013-2015: III/6/j; SF-SAC 2016-2018: III/1/b; SF-SAC 2019-2021: III/1/b; SF-SAC 2022: III/1/b Census mapping: CFDA INFO, TYPEREPORT_MP"
type_report_major_program_general = "Data sources: SF-SAC 1997-2000: III/1; SF-SAC 2001-2003: III/1 Census mapping: GENERAL, TYPEREPORT_MP"
type_requirement_cfdainfo = "Data sources: SF-SAC 1997-2000: III/7/b; SF-SAC 2001-2003: III/11/a; SF-SAC 2004-2007: III/10/a; SF-SAC 2008-2009: III/10/a; SF-SAC 2010-2012: III/10/a; SF-SAC 2013-2015: III/7/e; SF-SAC 2016-2018: III/4/f; SF-SAC 2019-2021: III/4/f; SF-SAC 2022: III/4/f Census mapping: CFDA INFO, TYPEREQUIREMENT"
type_requirement_findings = "Data sources: SF-SAC 2013-2015: III/7/e; SF-SAC 2016-2018: III/4/f; SF-SAC 2019-2021: III/4/f; SF-SAC 2022: III/4/f Census mapping: FINDINGS, TYPEREQUIREMENT"
duns_list = "Data sources: SF-SAC 2004-2007: I/5/git ad; SF-SAC 2008-2009: I/4/d; SF-SAC 2010-2012: I/4/d; SF-SAC 2013-2015: I/4/d; SF-SAC 2016-2018: I/4/d; SF-SAC 2019-2021: I/4/d; SF-SAC 2022: I/4/d Census mapping: GENERAL, DUNS (AND) Data sources: SF-SAC 2004-2007: I/5/f; SF-SAC 2008-2009: I/4/f; SF-SAC 2010-2012: I/4/f; SF-SAC 2013-2015: I/4/f; SF-SAC 2016-2018: I/4/f; SF-SAC 2019-2021: I/4/f; SF-SAC 2022: I/4/f Census mapping: DUN INFO, DUNS"
elec_audit_findings_id = "Census mapping: FINDINGS, ELECAUDITFINDINGSID"
material_weakness_findings = "Data sources: SF-SAC 2013-2015: III/7/h; SF-SAC 2016-2018: III/4/i; SF-SAC 2019-2021: III/4/i; SF-SAC 2022: III/4/i Census mapping: FINDINGS, MATERIALWEAKNESS"
material_weakness_general = "Data sources: SF-SAC 1997-2000: II/4; SF-SAC 2001-2003: II/4; SF-SAC 2004-2007: II/4; SF-SAC 2008-2009: II/4; SF-SAC 2010-2012: II/4; SF-SAC 2013-2015: II/4; SF-SAC 2016-2018: III/2/d; SF-SAC 2019-2021: III/2/d; SF-SAC 2022: III/2/d Census mapping: GENERAL, MATERIALWEAKNESS"
modified_opinion = "Data sources: SF-SAC 2013-2015: III/7/f; SF-SAC 2016-2018: III/4/g; SF-SAC 2019-2021: III/4/g; SF-SAC 2022: III/4/g Census mapping: FINDINGS, MODIFIEDOPINION"
other_findings = "Data sources: SF-SAC 2013-2015: III/7/j; SF-SAC 2016-2018: III/4/k; SF-SAC 2019-2021: III/4/k; SF-SAC 2022: III/4/k Census mapping: FINDINGS, OTHERFINDINGS"
other_non_compliance = "Data sources: SF-SAC 2013-2015: III/7/g; SF-SAC 2016-2018: III/4/h; SF-SAC 2019-2021: III/4/h; SF-SAC 2022: III/4/h Census mapping: FINDINGS, OTHERNONCOMPLIANCE"
prior_finding_ref_nums = "Data sources: SF-SAC 2016-2018: III/4/n; SF-SAC 2019-2021: III/4/n; SF-SAC 2022: III/4/n Census mapping: FINDINGS, PRIORFINDINGREFNUMS"
questioned_costs_findings = "Data sources: SF-SAC 2013-2015: III/7/k; SF-SAC 2016-2018: III/4/l; SF-SAC 2019-2021: III/4/l; SF-SAC 2022: III/4/l Census mapping: FINDINGS, QCOSTS"
questioned_costs_general = "Data sources: SF-SAC 2001-2003: III/7; SF-SAC 2004-2007: III/6; SF-SAC 2008-2009: III/6; SF-SAC 2010-2012: III/6 Census mapping: GENERAL, QCOSTS"
repeat_finding = "Data sources: SF-SAC 2016-2018: III/4/m; SF-SAC 2019-2021: III/4/m; SF-SAC 2022: III/4/m Census mapping: FINDINGS, REPEATFINDING"
significant_deficiency = "Data sources: SF-SAC 2013-2015: III/7/i; SF-SAC 2016-2018: III/4/j; SF-SAC 2019-2021: III/4/j; SF-SAC 2022: III/4/j Census mapping: FINDINGS, SIGNIFICANTDEFICIENCY"
auditee_certify_name = "Data sources: SF-SAC 1997-2000: I/6/g; SF-SAC 2001-2003: I/6/g; SF-SAC 2004-2007: I/6/g; SF-SAC 2008-2009: I/5/g; SF-SAC 2010-2012: I/5/g; SF-SAC 2013-2015: certifications; SF-SAC 2016-2018: certifications; SF-SAC 2019-2021: certifications; SF-SAC 2022: certifications Census mapping: GENERAL, AUDITEECERTIFYNAME"
auditee_certify_title = "Data sources: SF-SAC 1997-2000: I/6/g; SF-SAC 2001-2003: I/6/g; SF-SAC 2004-2007: I/6/g; SF-SAC 2008-2009: I/5/g; SF-SAC 2010-2012: I/5/g; SF-SAC 2013-2015: certifications; SF-SAC 2016-2018: certifications; SF-SAC 2019-2021: certifications; SF-SAC 2022: certifications Census mapping: GENERAL, AUDITEECERTIFYTITLE"
auditee_contact = "Data sources: SF-SAC 1997-2000: I/6/c; SF-SAC 2001-2003: I/6/c; SF-SAC 2004-2007: I/6/c; SF-SAC 2008-2009: I/5/c; SF-SAC 2010-2012: I/5/c; SF-SAC 2013-2015: I/5/c; SF-SAC 2016-2018: I/5/c; SF-SAC 2019-2021: I/5/c; SF-SAC 2022: I/5/c Census mapping: GENERAL, AUDITEECONTACT"
auditee_date_signed = "Data sources: SF-SAC 1997-2000: I/6/g; SF-SAC 2001-2003: I/6/g; SF-SAC 2004-2007: I/6/g; SF-SAC 2008-2009: I/5/g; SF-SAC 2010-2012: I/5/g; SF-SAC 2013-2015: certifications; SF-SAC 2016-2018: certifications; SF-SAC 2019-2021: certifications; SF-SAC 2022: certifications Census mapping: GENERAL, AUDITEEDATESIGNED"
auditee_email = "Data sources: SF-SAC 1997-2000: I/6/f; SF-SAC 2001-2003: I/6/f; SF-SAC 2004-2007: I/6/f; SF-SAC 2008-2009: I/5/f; SF-SAC 2010-2012: I/5/f; SF-SAC 2013-2015: I/5/f; SF-SAC 2016-2018: I/5/e; SF-SAC 2019-2021: I/5/e; SF-SAC 2022: I/5/e Census mapping: GENERAL, AUDITEEEMAIL"
auditee_fax = "Data sources: SF-SAC 1997-2000: I/6/e; SF-SAC 2001-2003: I/6/e; SF-SAC 2004-2007: I/6/e; SF-SAC 2008-2009: I/5/e; SF-SAC 2010-2012: I/5/e; SF-SAC 2013-2015: I/5/e Census mapping: GENERAL, AUDITEEFAX"
auditee_name = "Data sources: SF-SAC 1997-2000: I/6/a; SF-SAC 2001-2003: I/6/a; SF-SAC 2004-2007: I/6/a; SF-SAC 2008-2009: I/5/a; SF-SAC 2010-2012: I/5/a; SF-SAC 2013-2015: I/5/a; SF-SAC 2016-2018: I/5/a; SF-SAC 2019-2021: I/5/a; SF-SAC 2022: I/5/a Census mapping: GENERAL, AUDITEENAME"
auditee_name_title = "Data sources: SF-SAC 1997-2000: I/6/g; SF-SAC 2001-2003: I/6/g; SF-SAC 2004-2007: I/6/g; SF-SAC 2008-2009: I/5/g; SF-SAC 2010-2012: I/5/g; SF-SAC 2013-2015: certifications; SF-SAC 2016-2018: certifications; SF-SAC 2019-2021: certifications; SF-SAC 2022: certifications Census mapping: GENERAL, AUDITEENAMETITLE"
auditee_phone = "Data sources: SF-SAC 1997-2000: I/6/d; SF-SAC 2001-2003: I/6/d; SF-SAC 2004-2007: I/6/d; SF-SAC 2008-2009: I/5/d; SF-SAC 2010-2012: I/5/d; SF-SAC 2013-2015: I/5/d; SF-SAC 2016-2018: I/5/d; SF-SAC 2019-2021: I/5/d; SF-SAC 2022: I/5/d Census mapping: GENERAL, AUDITEEPHONE"
auditee_title = "Data sources: SF-SAC 1997-2000: I/6/c; SF-SAC 2001-2003: I/6/c; SF-SAC 2004-2007: I/6/c; SF-SAC 2008-2009: I/5/c; SF-SAC 2010-2012: I/5/c; SF-SAC 2013-2015: I/5/c; SF-SAC 2016-2018: I/5/c; SF-SAC 2019-2021: I/5/c; SF-SAC 2022: I/5/c Census mapping: GENERAL, AUDITEETITLE"
audit_type = "Data sources: SF-SAC 1997-2000: I/2; SF-SAC 2001-2003: I/2; SF-SAC 2004-2007: I/2; SF-SAC 2008-2009: I/2; SF-SAC 2010-2012: I/2; SF-SAC 2013-2015: I/2; SF-SAC 2016-2018: I/2; SF-SAC 2019-2021: I/2; SF-SAC 2022: I/2 Census mapping: GENERAL, AUDITTYPE"
city = "Data sources: SF-SAC 1997-2000: I/6/b; SF-SAC 2001-2003: I/6/b; SF-SAC 2004-2007: I/6/b; SF-SAC 2008-2009: I/5/b; SF-SAC 2010-2012: I/5/b; SF-SAC 2013-2015: I/5/b; SF-SAC 2016-2018: I/5/b; SF-SAC 2019-2021: I/5/b; SF-SAC 2022: I/5/b Census mapping: GENERAL, CITY"
cognizant_agency = "Data sources: SF-SAC 1997-2000: I/9; SF-SAC 2001-2003: I/9 Census mapping: GENERAL, COGAGENCY"
completed_on = "Census mapping: GENERAL, COMPLETED_ON"
component_date_received = "Census mapping: GENERAL, COMPONENT DATE RECEIVED"
auditor_city = "Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPACITY (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/d; SF-SAC 2016-2018: I/8/d; SF-SAC 2019-2021: I/6/h/iv; SF-SAC 2022: I/6/h/iv Census mapping: MULTIPLE CPAS INFO, CPACITY"
auditor_contact = "Data sources: SF-SAC 1997-2000: I/7/c; SF-SAC 2001-2003: I/7/c; SF-SAC 2004-2007: I/7/c; SF-SAC 2008-2009: I/6/c; SF-SAC 2010-2012: I/6/c; SF-SAC 2013-2015: I/6/d; SF-SAC 2016-2018: I/6/d; SF-SAC 2019-2021: I/6/d; SF-SAC 2022: I/6/d Census mapping: GENERAL, CPACONTACT (AND) Data sources: SF-SAC 2008-2009: I/8/c; SF-SAC 2010-2012: I/8/c; SF-SAC 2013-2015: I/8/g; SF-SAC 2016-2018: I/8/g; SF-SAC 2019-2021: I/6/h/vii; SF-SAC 2022: I/6/h/vii Census mapping: MULTIPLE CPAS INFO, CPACONTACT"
auditor_country = "Data sources: SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPACOUNTRY"
auditor_date_signed = "Data sources: SF-SAC 1997-2000: I/7/g; SF-SAC 2001-2003: I/7/g; SF-SAC 2004-2007: I/7/g; SF-SAC 2008-2009: I/6/g; SF-SAC 2010-2012: I/6/g; SF-SAC 2013-2015: certifications; SF-SAC 2016-2018: certifications; SF-SAC 2019-2021: certifications; SF-SAC 2022: certifications Census mapping: GENERAL, CPADATESIGNED"
auditor_email = "Data sources: SF-SAC 1997-2000: I/7/f; SF-SAC 2001-2003: I/7/f; SF-SAC 2004-2007: I/7/f; SF-SAC 2008-2009: I/6/f; SF-SAC 2010-2012: I/6/f; SF-SAC 2013-2015: I/6/g; SF-SAC 2016-2018: I/6/f; SF-SAC 2019-2021: I/6/f; SF-SAC 2022: I/6/f Census mapping: GENERAL, CPAEMAIL (AND) Data sources: SF-SAC 2008-2009: I/8/f; SF-SAC 2010-2012: I/8/f; SF-SAC 2013-2015: I/8/k; SF-SAC 2016-2018: I/8/k; SF-SAC 2019-2021: I/6/h/x; SF-SAC 2022: I/6/h/x Census mapping: MULTIPLE CPAS INFO, CPAEMAIL"
auditor_fax = "Data sources: SF-SAC 1997-2000: I/7/e; SF-SAC 2001-2003: I/7/e; SF-SAC 2004-2007: I/7/e; SF-SAC 2008-2009: I/6/e; SF-SAC 2010-2012: I/6/e; SF-SAC 2013-2015: I/6/f Census mapping: GENERAL, CPAFAX (AND) Data sources: SF-SAC 2008-2009: I/8/e; SF-SAC 2010-2012: I/8/e; SF-SAC 2013-2015: I/8/j; SF-SAC 2016-2018: I/8/j Census mapping: MULTIPLE CPAS INFO, CPAFAX"
auditor_firm_name = "Data sources: SF-SAC 1997-2000: I/7/a; SF-SAC 2001-2003: I/7/a; SF-SAC 2004-2007: I/7/a; SF-SAC 2008-2009: I/6/a; SF-SAC 2010-2012: I/6/a; SF-SAC 2013-2015: I/6/a; SF-SAC 2016-2018: I/6/a; SF-SAC 2019-2021: I/6/a; SF-SAC 2022: I/6/a Census mapping: GENERAL, CPAFIRMNAME (AND) Data sources: SF-SAC 2008-2009: I/8/a; SF-SAC 2010-2012: I/8/a; SF-SAC 2013-2015: I/8/a; SF-SAC 2016-2018: I/8/a; SF-SAC 2019-2021: I/6/h/i; SF-SAC 2022: I/6/h/i Census mapping: MULTIPLE CPAS INFO, CPAFIRMNAME"
auditor_foreign = "Data sources: SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPAFOREIGN"
auditor_phone = "Data sources: SF-SAC 1997-2000: I/7/d; SF-SAC 2001-2003: I/7/d; SF-SAC 2004-2007: I/7/d; SF-SAC 2008-2009: I/6/d; SF-SAC 2010-2012: I/6/d; SF-SAC 2013-2015: I/6/e; SF-SAC 2016-2018: I/6/e; SF-SAC 2019-2021: I/6/e; SF-SAC 2022: I/6/e Census mapping: GENERAL, CPAPHONE (AND) Data sources: SF-SAC 2008-2009: I/8/d; SF-SAC 2010-2012: I/8/d; SF-SAC 2013-2015: I/8/i; SF-SAC 2016-2018: I/8/i; SF-SAC 2019-2021: I/6/h/ix; SF-SAC 2022: I/6/h/ix Census mapping: MULTIPLE CPAS INFO, CPAPHONE"
auditor_state = "Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPASTATE (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/e; SF-SAC 2016-2018: I/8/e; SF-SAC 2019-2021: I/6/h/v; SF-SAC 2022: I/6/h/v Census mapping: MULTIPLE CPAS INFO, CPASTATE"
auditor_street1 = "Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPASTREET1 (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/c; SF-SAC 2016-2018: I/8/c; SF-SAC 2019-2021: I/6/h/iii; SF-SAC 2022: I/6/h/iii Census mapping: MULTIPLE CPAS INFO, CPASTREET1"
auditor_street2 = "Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPASTREET2"
auditor_title = "Data sources: SF-SAC 1997-2000: I/7/c; SF-SAC 2001-2003: I/7/c; SF-SAC 2004-2007: I/7/c; SF-SAC 2008-2009: I/6/c; SF-SAC 2010-2012: I/6/c; SF-SAC 2013-2015: I/6/d; SF-SAC 2016-2018: I/6/d; SF-SAC 2019-2021: I/6/d; SF-SAC 2022: I/6/d Census mapping: GENERAL, CPATITLE (AND) Data sources: SF-SAC 2008-2009: I/8/c; SF-SAC 2010-2012: I/8/c; SF-SAC 2013-2015: I/8/h; SF-SAC 2016-2018: I/8/h; SF-SAC 2019-2021: I/6/h/viii; SF-SAC 2022: I/6/h/viii Census mapping: MULTIPLE CPAS INFO, CPATITLE"
auditor_zip_code = "Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPAZIPCODE (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/f; SF-SAC 2016-2018: I/8/f; SF-SAC 2019-2021: I/6/h/vi; SF-SAC 2022: I/6/h/vi Census mapping: MULTIPLE CPAS INFO, CPAZIPCODE"
current_or_former_findings = "Data sources: SF-SAC 2001-2003: III/9; SF-SAC 2004-2007: III/8; SF-SAC 2008-2009: III/8; SF-SAC 2010-2012: III/8; SF-SAC 2013-2015: III/5; SF-SAC 2016-2018: III/3/d; SF-SAC 2019-2021: III/3/d; SF-SAC 2022: III/3/d Census mapping: GENERAL, CYFINDINGS"
dollar_threshold = "Data sources: SF-SAC 1997-2000: III/2; SF-SAC 2001-2003: III/3; SF-SAC 2004-2007: III/2; SF-SAC 2008-2009: III/2; SF-SAC 2010-2012: III/2; SF-SAC 2013-2015: III/2; SF-SAC 2016-2018: III/3/b; SF-SAC 2019-2021: III/3/b; SF-SAC 2022: III/3/b Census mapping: GENERAL, DOLLARTHRESHOLD"
dup_reports = "Data sources: SF-SAC 2001-2003: III/2; SF-SAC 2004-2007: III/1; SF-SAC 2008-2009: III/1; SF-SAC 2010-2012: III/1; SF-SAC 2013-2015: III/1; SF-SAC 2016-2018: III/3/a; SF-SAC 2019-2021: III/3/a; SF-SAC 2022: III/3/a Census mapping: GENERAL, DUP_REPORTS"
ein_subcode = "Census mapping: GENERAL, EINSUBCODE"
entity_type = "Census mapping: GENERAL, ENTITY_TYPE"
fac_accepted_date = "Census mapping: GENERAL, FACACCEPTEDDATE"
form_date_received = "Census mapping: GENERAL, FORM DATE RECEIVED"
fy_end_date = "Data sources: SF-SAC 1997-2000: Part I, Item 1; SF-SAC 2001-2003: Part I, Item 1; SF-SAC 2004-2007: Part I, Item 1; SF-SAC 2008-2009: Part I, Item 1; SF-SAC 2010-2012: Part I, Item 1; SF-SAC 2013-2015: Part I, Item 1; SF-SAC 2016-2018: Part I, Item 1; SF-SAC 2019-2021: I/1/b; SF-SAC 2022: I/1/b Census mapping: GENERAL, FYENDDATE"
fy_start_date = "Data sources: SF-SAC 2019-2021: Part I, Item 1(a); SF-SAC 2022: Part I, Item 1(a) Census mapping: GENERAL, FYSTARTDATE"
going_concern = "Data sources: SF-SAC 1997-2000: II/2; SF-SAC 2001-2003: II/2; SF-SAC 2004-2007: II/2; SF-SAC 2008-2009: II/2; SF-SAC 2010-2012: II/2; SF-SAC 2013-2015: II/2; SF-SAC 2016-2018: III/2/b; SF-SAC 2019-2021: III/2/b; SF-SAC 2022: III/2/b Census mapping: GENERAL, GOINGCONCERN"
initial_date_received = "Census mapping: GENERAL, INITIAL DATE RECEIVED"
low_risk = "Data sources: SF-SAC 1997-2000: III/3; SF-SAC 2001-2003: III/4; SF-SAC 2004-2007: III/3; SF-SAC 2008-2009: III/3; SF-SAC 2010-2012: III/3; SF-SAC 2013-2015: III/3; SF-SAC 2016-2018: III/3/c; SF-SAC 2019-2021: III/3/c; SF-SAC 2022: III/3/c Census mapping: GENERAL, LOWRISK"
material_noncompliance = "Data sources: SF-SAC 1997-2000: II/5; SF-SAC 2001-2003: II/5; SF-SAC 2004-2007: II/5; SF-SAC 2008-2009: II/5; SF-SAC 2010-2012: II/5; SF-SAC 2013-2015: II/5; SF-SAC 2016-2018: III/2/e; SF-SAC 2019-2021: III/2/e; SF-SAC 2022: III/2/e Census mapping: GENERAL, MATERIALNONCOMPLIANCE"
material_weakness_major_program = "Data sources: SF-SAC 2001-2003: III/6; SF-SAC 2004-2007: III/5; SF-SAC 2008-2009: III/5; SF-SAC 2010-2012: III/5 Census mapping: GENERAL, MATERIALWEAKNESS_MP"
multiple_cpas = "Data sources: SF-SAC 2008-2009: I/7/a; SF-SAC 2010-2012: I/7/a; SF-SAC 2013-2015: I/7; SF-SAC 2016-2018: I/7; SF-SAC 2019-2021: I/6/g; SF-SAC 2022: I/6/g Census mapping: GENERAL, MULTIPLE_CPAS"
multiple_duns = "Data sources: SF-SAC 2004-2007: I/5/e; SF-SAC 2008-2009: I/4/e; SF-SAC 2010-2012: I/4/e; SF-SAC 2013-2015: I/4/e; SF-SAC 2016-2018: I/4/e; SF-SAC 2019-2021: I/4/e; SF-SAC 2022: I/4/e Census mapping: GENERAL, MULTIPLEDUNS"
multiple_eins = "Data sources: SF-SAC 1997-2000: I/5/b; SF-SAC 2001-2003: I/5/b; SF-SAC 2004-2007: I/5/b; SF-SAC 2008-2009: I/4/b; SF-SAC 2010-2012: I/4/b; SF-SAC 2013-2015: I/4/b; SF-SAC 2016-2018: I/4/b; SF-SAC 2019-2021: I/4/b; SF-SAC 2022: I/4/b Census mapping: GENERAL, MULTIPLEEINS"
multiple_ueis = "Data sources: SF-SAC 2022: I/4/h Census mapping: GENERAL, MULTIPLEUEIS"
number_months = "Data sources: SF-SAC 1997-2000: I/3; SF-SAC 2001-2003: I/3; SF-SAC 2004-2007: I/3; SF-SAC 2008-2009: I/3; SF-SAC 2010-2012: I/3; SF-SAC 2013-2015: I/3; SF-SAC 2016-2018: I/3; SF-SAC 2019-2021: I/3; SF-SAC 2022: I/3 Census mapping: GENERAL, NUMBERMONTHS"
oversight_agency = "Data sources: SF-SAC 1997-2000: I/9; SF-SAC 2001-2003: I/9 Census mapping: GENERAL, OVERSIGHTAGENCY"
period_covered = "Data sources: SF-SAC 1997-2000: I/3; SF-SAC 2001-2003: I/3; SF-SAC 2004-2007: I/3; SF-SAC 2008-2009: I/3; SF-SAC 2010-2012: I/3; SF-SAC 2013-2015: I/3; SF-SAC 2016-2018: I/3; SF-SAC 2019-2021: I/3; SF-SAC 2022: I/3 Census mapping: GENERAL, PERIODCOVERED"
previous_completed_on = "Census mapping: GENERAL, PREVIOUS_COMPLETED_ON"
prior_year_schedule = "Data sources: SF-SAC 2001-2003: III/8; SF-SAC 2004-2007: III/7; SF-SAC 2008-2009: III/7; SF-SAC 2010-2012: III/7; SF-SAC 2013-2015: III/4 Census mapping: GENERAL, PYSCHEDULE"
reportable_condition = "Data sources: SF-SAC 1997-2000: II/3; SF-SAC 2001-2003: II/3; SF-SAC 2004-2007: II/3; SF-SAC 2008-2009: II/3; SF-SAC 2010-2012: II/3; SF-SAC 2013-2015: II/3; SF-SAC 2016-2018: III/2/c; SF-SAC 2019-2021: III/2/c; SF-SAC 2022: III/2/c Census mapping: GENERAL, REPORTABLECONDITION"
significant_deficiency_general = "Data sources: SF-SAC 1997-2000: II/3; SF-SAC 2001-2003: II/3; SF-SAC 2004-2007: II/3; SF-SAC 2008-2009: II/3; SF-SAC 2010-2012: II/3; SF-SAC 2013-2015: II/3; SF-SAC 2016-2018: III/2/c; SF-SAC 2019-2021: III/2/c; SF-SAC 2022: III/2/c Census mapping: GENERAL, SIGNIFICANTDEFICIENCY"
significant_deficiency_findings = "Data sources: SF-SAC 1997-2000: II/3; SF-SAC 2001-2003: II/3; SF-SAC 2004-2007: II/3; SF-SAC 2008-2009: II/3; SF-SAC 2010-2012: II/3; SF-SAC 2013-2015: II/3; SF-SAC 2016-2018: III/2/c; SF-SAC 2019-2021: III/2/c; SF-SAC 2022: III/2/c Census mapping: FINDINGS, SIGNIFICANTDEFICIENCY"
reportable_condition_major_program = "Data sources: SF-SAC 2001-2003: III/5; SF-SAC 2004-2007: III/4; SF-SAC 2008-2009: III/4; SF-SAC 2010-2012: III/4 Census mapping: GENERAL, REPORTABLECONDITION_MP"
report_required = "Data sources: SF-SAC 1997-2000: III/5; SF-SAC 2001-2003: III/9; SF-SAC 2004-2007: III/8 Census mapping: GENERAL, REPORTREQUIRED"
sp_framework = "Data sources: SF-SAC 2016-2018: III/2/a/ii; SF-SAC 2019-2021: III/2/a/i; SF-SAC 2022: III/2/a/i Census mapping: GENERAL, SP_FRAMEWORK"
sp_framework_required = "Data sources: SF-SAC 2016-2018: III/2/a/iii; SF-SAC 2019-2021: III/2/a/ii; SF-SAC 2022: III/2/a/ii Census mapping: GENERAL, SP_FRAMEWORK_REQUIRED"
state = "Data sources: SF-SAC 1997-2000: I/6/b; SF-SAC 2001-2003: I/6/b; SF-SAC 2004-2007: I/6/b; SF-SAC 2008-2009: I/5/b; SF-SAC 2010-2012: I/5/b; SF-SAC 2013-2015: I/5/b; SF-SAC 2016-2018: I/5/b; SF-SAC 2019-2021: I/5/b; SF-SAC 2022: I/5/b Census mapping: GENERAL, STATE"
street1 = "Data sources: SF-SAC 1997-2000: I/6/b; SF-SAC 2001-2003: I/6/b; SF-SAC 2004-2007: I/6/b; SF-SAC 2008-2009: I/5/b; SF-SAC 2010-2012: I/5/b; SF-SAC 2013-2015: I/5/b; SF-SAC 2016-2018: I/5/b; SF-SAC 2019-2021: I/5/b; SF-SAC 2022: I/5/b Census mapping: GENERAL, STREET1"
street2 = "Data sources: SF-SAC 1997-2000: I/6/b; SF-SAC 2001-2003: I/6/b; SF-SAC 2004-2007: I/6/b; SF-SAC 2008-2009: I/5/b; SF-SAC 2010-2012: I/5/b; SF-SAC 2013-2015: I/5/b; SF-SAC 2016-2018: I/5/b; SF-SAC 2019-2021: I/5/b; SF-SAC 2022: I/5/b Census mapping: GENERAL, STREET2"
total_fed_expenditures = "Data sources: SF-SAC 1997-2000: III/6/c- Total; SF-SAC 2001-2003: III/10/d -Total; SF-SAC 2004-2007: III/9/e -Total; SF-SAC 2008-2009: III/9/e -Total; SF-SAC 2010-2012: III/9/f -Total; SF-SAC 2013-2015: III/6/d -Total; SF-SAC 2016-2018: II/1/e- Total; SF-SAC 2019-2021: II/1/e - Total; SF-SAC 2022: II/1/e - Total Census mapping: GENERAL, TOTFEDEXPEND"
type_of_entity = "Census mapping: GENERAL, TYPEOFENTITY"
type_report_financial_statements = "Data sources: SF-SAC 1997-2000: II/1; SF-SAC 2001-2003: II/1; SF-SAC 2004-2007: II/1; SF-SAC 2008-2009: II/1; SF-SAC 2010-2012: II/1; SF-SAC 2013-2015: II/1; SF-SAC 2016-2018: III/2/a/i; SF-SAC 2019-2021: III/2/a; SF-SAC 2022: III/2/a Census mapping: GENERAL, TYPEREPORT_FS"
type_report_special_purpose_framework = "Data sources: SF-SAC 2016-2018: III/2/a/iv; SF-SAC 2019-2021: III/2/a/iii; SF-SAC 2022: III/2/a/iii Census mapping: GENERAL, TYPEREPORT_SP_FRAMEWORK"
uei_general = "Data sources: SF-SAC 2022: I/4/g Census mapping: GENERAL, UEI"
uei_ueiinfo = "Data sources: SF-SAC 2004-2007: I/5/f; SF-SAC 2008-2009: I/4/f; SF-SAC 2010-2012: I/4/f; SF-SAC 2013-2015: I/4/f; SF-SAC 2016-2018: I/4/f; SF-SAC 2019-2021: I/4/f; SF-SAC 2022: I/4/i Census mapping: UEI INFO, UEI"
zip_code = "Data sources: SF-SAC 1997-2000: I/6/b; SF-SAC 2001-2003: I/6/b; SF-SAC 2004-2007: I/6/b; SF-SAC 2008-2009: I/5/b; SF-SAC 2010-2012: I/5/b; SF-SAC 2013-2015: I/5/b; SF-SAC 2016-2018: I/5/b; SF-SAC 2019-2021: I/5/b; SF-SAC 2022: I/5/b Census mapping: GENERAL, ZIPCODE"
auditor_ein = "Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN (AND) Data sources: SF-SAC 2013-2015: I/8/b; SF-SAC 2016-2018: I/8/b; SF-SAC 2019-2021: I/6/h/ii; SF-SAC 2022: I/6/h/ii Census mapping: MULTIPLE CPAS INFO, CPAEIN"
seqnum = (
    "Census mapping: GENERAL, SEQNUM (AND) Census mapping: MULTIPLE CPAS INFO, SEQNUM"
)
content = "Data sources: SF-SAC 2019-2021: II/2; SF-SAC 2022: II/2 Census mapping: NOTES, CONTENT"
fac_id = "Census mapping: NOTES, ID"
note_index = "Census mapping: NOTES, NOTE_INDEX"
report_id = "Census mapping: NOTES, REPORTID"
title = "Data sources: SF-SAC 2019-2021: II/2; SF-SAC 2022: II/2 Census mapping: NOTES, TITLE"
type_id = "Census mapping: NOTES, TYPE_ID"
version = "Census mapping: NOTES, VERSION"
passthrough_id = "Data sources: SF-SAC 2016-2018: II/1/m; SF-SAC 2019-2021: II/1/m; SF-SAC 2022: II/1/m Census mapping: PASSTHROUGH, PASSTHROUGHID"
passthrough_name = "Data sources: SF-SAC 2016-2018: II/1/l; SF-SAC 2019-2021: II/1/l; SF-SAC 2022: II/1/l Census mapping: PASSTHROUGH, PASSTHROUGHNAME"
audit_info = "Census mapping: REVISIONS, AUDITINFO"
auditinfo_explain = "Census mapping: REVISIONS, AUDITINFO_EXPLAIN"
cap = "Census mapping: REVISIONS, CAP"
cap_explain = "Census mapping: REVISIONS, CAP_EXPLAIN"
elec_report_revision_id = "Census mapping: REVISIONS, ELECRPTREVISIONID"
federal_awards = "Census mapping: REVISIONS, FEDERALAWARDS"
federal_awards_explain = "Census mapping: REVISIONS, FEDERALAWARDS_EXPLAIN"
findings = "Census mapping: CFDA INFO, FINDINGS"
findings_revisions = "Census mapping: REVISIONS, FINDINGS"
findings_explain = "Census mapping: REVISIONS, FINDINGS_EXPLAIN"
findings_text = "Census mapping: REVISIONS, FINDINGSTEXT"
findings_text_explain = "Census mapping: REVISIONS, FINDINGSTEXT_EXPLAIN"
general_info = "Census mapping: REVISIONS, GENINFO"
general_info_explain = "Census mapping: REVISIONS, GENINFO_EXPLAIN"
notes_to_sefa = "Census mapping: REVISIONS, NOTESTOSEFA"
notes_to_sefa_explain = "Census mapping: REVISIONS, NOTESTOSEFA_EXPLAIN"
other = "Census mapping: REVISIONS, OTHER"
other_explain = "Census mapping: REVISIONS, OTHER_EXPLAIN"
uei_seq_num = "Census mapping: UEI INFO, UEISEQNUM"
# adding manually
cognizant_agency_over = "Census mapping: GENERAL, COG_OVER"
date_firewall = "Census mapping: GENERAL, DATEFIREWALL"
previous_date_firewall = "Census mapping: GENERAL, PREVIOUSDATEFIREWALL"
questioned_costs_FederalAward = "Census mapping: CFDA INFO, QCOSTS2"
