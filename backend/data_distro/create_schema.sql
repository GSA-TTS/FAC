/*
I am creating tables Rick suggested and then making models out of them. I think I will then delete the original tables. I will use the models to generate the tables and then we can have them as managed tables by Django going forward.

I added "data_distro_" so when I use django inspect I can grab all the related models in a way that is easy to identify.
*/

/*
    New table to normalize entity types

    INSERT INTO entity_types(identifier, name) VALUES (0,'State-Wide');
    INSERT INTO entity_types(identifier, name) VALUES (1,'State-Dependent Airport Authority');
    INSERT INTO entity_types(identifier, name) VALUES (2,'State-Dependent Hospital');
    INSERT INTO entity_types(identifier, name) VALUES (3,'State-Dependent Housing Authority');
    ...

*/

CREATE TABLE data_distro_entity_types
(
    id SERIAL NOT NULL PRIMARY KEY,
    identifier SMALLINT NOT NULL,
    name text NOT NULL
);


/*
    This table extracts auditee information from the old ELECAUDITHEADER table
*/


CREATE TABLE data_distro_auditees
(
    id SERIAL NOT NULL PRIMARY KEY,
    name text NULL,
    street1 text NULL,
    street2 text NULL,
    city text NULL,
    state text NULL,
    zipcode text NULL,
    contact text NULL,
    title text NULL,
    phone text NULL,
    fax text NULL,
    email text NULL
);


/*
    This table extracts primary information from the old ELECAUDITHEADER table
    Shift from ReportId/Version for key -> generic id

    CPAS for CPA info
*/

CREATE TABLE data_distro_audits
(
    auditid SERIAL NOT NULL PRIMARY KEY,
    auditeeid BIGINT NOT NULL,
    audit_year SMALLINT NOT NULL,
    reportid INTEGER NOT NULL,
    version SMALLINT NOT NULL DEFAULT 1,
    entity_type_id SMALLINT NULL,
    fyenddate DATE NULL,
    audittype text NOT NULL,
    periodcovered text NULL,
    numberofmonths SMALLINT NULL,
    auditee_date_signed date NULL,
    cpa_date_signed date NULL,
    cog_agency text NULL,
    oversight_agency text NULL,
    completed_on date NULL,
    previously_completed_on date NULL,
    fac_accepted_date date NULL,
    dollar_threshhold money NULL,
    total_federal_expenditure money NULL,
    CONSTRAINT fk_audit_et FOREIGN KEY (entity_type_id) REFERENCES data_distro_entity_types(id),
    CONSTRAINT fk_audit_auditee FOREIGN KEY (auditeeid) REFERENCES data_distro_auditees(id)
);

/*
    This table represents refactored version of ELECREPORTAGENCIES
*/


CREATE TABLE data_distro_agencies
(
  id SERIAL NOT NULL PRIMARY KEY,
  auditid BIGINT NOT NULL,
  agency_cfda text,
  prior_agency text,
  prior_finding  boolean null,
  current_finding  boolean null,
  CONSTRAINT fk_audits_agencies FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);


-- Starting with the ones above


    -- This table represents refactored version of ELECPDF_METADATA


/*
    This table is only valuable when an upload mystery occurs or
    when general upload metrics are needed. Legacy team probably looks at
    this table once or twice a year.
*/



CREATE TABLE data_distro_pdf_metadata
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    filename text not null,
    searchable_threshold smallint,
    searchable_type text,
    searchable_percentage smallint,
    image_only_page_numbers text,
    processing_time_milliseconds INTEGER,
    upload_attempts smallint,
    upload_status text,
    upload_date TIMESTAMP NOT NULL,
    title text,
    author text,
    subject text,
    keywords text,
    create_date TIMESTAMP NOT NULL,
    modification_date TIMESTAMP,
    producer text,
    page_count smallint,
    file_size INTEGER,
    printable BOOLEAN,
    printable_high_quality BOOLEAN,
    modifiable BOOLEAN,
    err_code text,
    CONSTRAINT fk_pdfmeta_audits FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);

/*
    This table represents refactored version of ELECAUDITS

    Captext for FINDINGREFNUMS?
    CFDA Clustername, Findings, Pass through total and amount form
*/

CREATE TABLE data_distro_awards
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    cfda text NOT NULL,
    award_identification text null,
    loan_balance text null,
    federal_program_name text not null,
    amount money not null,
    clustername text null,
    stateclustername text null,
    progam_total MONEY null,
    cluster_total MONEY null,
    passthrough_award text null,
    passthrough_amount MONEY null,
    findingrefnums text null,
    findings_count smallint,
    CONSTRAINT fk_audits_awards FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);

/*
    This table represents refactored version of ELECPASSTHROUGHS
*/

CREATE TABLE data_distro_passthroughs
(
    id SERIAL NOT NULL PRIMARY KEY,
    awardid BIGINT NOT NULL,
    name text,
    passid text,
    CONSTRAINT fk_passthrough_awards FOREIGN KEY (awardid) REFERENCES data_distro_awards (id)
);

/*
    This table represents refactored version of ELECNOTES
*/

CREATE TABLE data_distro_notes_type
(
    id SERIAL NOT NULL PRIMARY KEY,
    name text NOT NULL
);

/*
Notes table
*/


CREATE TABLE data_distro_notes
(
    id SERIAL NOT NULL PRIMARY KEY,
    typeid BIGINT NOT NULL,
    auditid BIGINT NOT NULL,
    content text not null,
    note_index smallint not null default 1,
    title text not null,
    CONSTRAINT fk_notes_audits FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid),
    CONSTRAINT fk_notes_type FOREIGN KEY (typeid) REFERENCES data_distro_notes_type(id)
);

-- Did not load this for now
INSERT INTO notes_type(NAME) VALUES ('ACOUNTING STANDARDS');
INSERT INTO notes_type(NAME) VALUES ('10% RULE');
INSERT INTO notes_type(NAME) VALUES ('ADDITIONAL');
INSERT INTO notes_type(NAME) VALUES ('SPECIAL');

/*
    This table represents refactored version of ELECFINDINGTEXT
*/

CREATE TABLE data_distro_findings_text
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    charts_tables boolean default false,
    text_value text,
    finding_ref_numbers text,
    CONSTRAINT fk_findtxt_audits FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);


/*
    This table represents refactored version of ELECDUNS
*/

CREATE TABLE data_distro_duns
(
    id SERIAL NOT NULL PRIMARY KEY,
    dun text NOT NULL
);

/*
    This table represents refactored version of ELECCAPTEXT
*/

CREATE TABLE cdata_distro_ap_text
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    charts_tables boolean default false,
    text_value text,
    finding_ref_numbers text,
    CONSTRAINT fk_captxt_audits FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);



/*
    This table represents indicator fields extracted from the ELECAUDITS TABLE to further
    normalize the indicator structure for awards
    Booleans not defaulted to null due to "not answered" indication

    FINDINGSTEXT seems to match
*/

CREATE TABLE data_distro_award_indicators
(
    id SERIAL NOT NULL PRIMARY KEY,
    awardid BIGINT NOT NULL,
    rd boolean null,
    loans boolean null,
    direct boolean null,
    arra boolean null,
    major_program boolean null,
    findings text,
    typereport_major_program text null,
    type_requirement text null,
    CONSTRAINT fk_indicators_award FOREIGN KEY (awardid) REFERENCES data_distro_awards(id)
);


/*
    This table represents refactored version of ELECAUDITFINDINGS

    captext for FINDINGREFNUMS
*/


CREATE TABLE data_distro_award_findings
(
    id SERIAL NOT NULL PRIMARY KEY,
    awardid BIGINT NOT NULL,
    fac_audit_id bigint NOT NULL,
    findingrefnums text null,
    type_requirement text null,
    modified_opinion text null,
    other_noncompliance text null,
    material_weakness text null,
    significant_deficiency text null,
    other_findings text null,
    qcosts text null,
    repeat_finding text null,
    priorfindingrefnums text null,
    CONSTRAINT fk_award_findings FOREIGN KEY (awardid) REFERENCES data_distro_awards(id)
);

/*
    This table represents refactored version of ELECEINS
*/

CREATE TABLE data_distro_eins
(
    id SERIAL NOT NULL PRIMARY KEY,
    ein text NOT NULL
);


/*
    New table that refines the old ELECEINS and removes duplication

    Seems to match agency table in downloads
*/
CREATE TABLE data_distro_audit_eins
(
    auditid BIGINT NOT NULL,
    einid BIGINT NOT NULL,
    is_primary boolean NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_ae_au FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid),
    CONSTRAINT fk_ae_eins FOREIGN KEY (einid) REFERENCES data_distro_eins(id)
);

/*
    New table that refines the old ELECDUNS and removes duplication

    Seems to match Duns table in downloads
*/
CREATE TABLE data_distro_audit_duns
(
    auditid BIGINT NOT NULL,
    dunid BIGINT NOT NULL,
    is_primary boolean NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_ad_au FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid),
    CONSTRAINT fk_ad_duns FOREIGN KEY (dunid) REFERENCES data_distro_duns(id)
);

/*
    This table represents refactored version of ELECCPAS
*/

CREATE TABLE data_distro_auditors
(
    id SERIAL NOT NULL PRIMARY KEY,
    seqnum SMALLINT NULL,
    firmname text NOT NULL,
    ein text  NULL,
    street1 text,
    street2 text,
    city text,
    state text,
    zipcode text,
    contact text,
    title text,
    phone text,
    fax text,
    email text
);

/*
    New table that refines the old ELECCPAS and removes duplication
*/
CREATE TABLE data_distro_audit_auditors
(
    auditid BIGINT NOT NULL,
    auditorid BIGINT NOT NULL,
    is_primary boolean NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_aa_au_tors FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid),
    CONSTRAINT fk_aa_tors FOREIGN KEY (auditorid) REFERENCES data_distro_auditors(id)
);

/*
    This table represents refactored version of IDES_SHISTORY
    I have not added legacy fields that have not been used pre 2016 and also
    have removed redundent fields (contained in other table structures or
    are calculated columns)
*/

CREATE TABLE data_distro_audit_status
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    final BOOLEAN,
    audit_uploaded BOOLEAN,
    audit_upload_date TIMESTAMP,
    auditee_submitted BOOLEAN,
    auditee_submit_date TIMESTAMP,
    auditor_submitted BOOLEAN,
    auditor_submit_date TIMESTAMP,
    fac_submit BOOLEAN,
    fac_submit_date TIMESTAMP,
    created TIMESTAMP,
    modified TIMESTAMP,
    submitted BOOLEAN,
    CONSTRAINT fk_status_audits FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);

/*
    This table represents refactored version of ELECRPT_REVISIONS

    REVISIONS table
*/

CREATE TABLE data_distro_audit_revisions
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    general_info text,
    general_info_explain text,
    federal_awards text,
    federal_awards_explain text,
    findings text,
    findings_explain text,
    findings_text text,
    findings_text_explain text,
    audit_info text,
    audit_info_explain text,
    cap text,
    cap_explain text,
    notes_to_sefa text,
    notes_to_sefa_explain text,
    other text,
    other_explain text,
    CONSTRAINT fk_revisions_audits FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);



/*
    This table represents indicator fields extracted from the ELECAUDITHEADER TABLE to further
    normalize the indicator structure
    Booleans not defaulted to null due to "not answered" indication

    Seems to match the GEN table in downloads
*/

CREATE TABLE data_distro_audit_indicators
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    type_report_financial_statements text null,
    special_framework text null,
    special_framework_required boolean null,
    typereport_special_framework text null,
    going_concern boolean null,
    material_weakness boolean null,
    material_non_compliance boolean null,
    type_report_major_program text  null,
    lowrisk boolean null,
    material_weakness_major_program boolean null,
    qcosts boolean null,
    reportable_condition boolean null,
    reportable_condition_major_program boolean null,
    significant_deficiency boolean null,
    significant_deficiency_material_weakness  boolean null,
    significant_deficiency_major_program  boolean null,
    cyfindings boolean null,
    pyschedule boolean null,
    CONSTRAINT fk_audits_indicators FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);

/*
    This table represents refactored version of ELECCOMPONENTS
*/

CREATE TABLE data_distro_audit_components
(
    id SERIAL NOT NULL PRIMARY KEY,
    auditid BIGINT NOT NULL,
    cap text,
    financial_statements text,
    sefa text,
    schedule_prior_audit_findings text,
    opinion_on_financial_statements text,
    report_internal_control text,
    gasreport_on_compliance text,
    sfqc text,
    opinion_or_disclaimer_sfa text,
    gasreport_internal_control text,
    report_on_compliance text,
    CONSTRAINT fk_compp_audits FOREIGN KEY (auditid) REFERENCES data_distro_audits(auditid)
);
