
begin;


---------------------------------------
-- accesses
---------------------------------------
-- public.audit_access definition

-- Drop table

-- DROP TABLE public.audit_access;

CREATE OR REPLACE VIEW admin_api_v2_0_0.audit_access AS
    SELECT
        aa.role,
        aa.fullname,
        aa.email,
        aa.sac_id,
        aa.user_id
    FROM
        public.audit_access aa
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY aa.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.singleauditchecklist AS
    SELECT
        sac.id,
        sac.date_created,
        sac.submission_status,
        sac.data_source,
        sac.transition_name,
        sac.transition_date,
        sac.report_id,
        sac.audit_type,
        sac.general_information,
        sac.audit_information,
        sac.federal_awards,
        sac.corrective_action_plan,
        sac.findings_text,
        sac.findings_uniform_guidance,
        sac.additional_ueis,
        sac.additional_eins,
        sac.secondary_auditors,
        sac.notes_to_sefa,
        sac.auditor_certification,
        sac.auditee_certification,
        sac.tribal_data_consent,
        sac.cognizant_agency,
        sac.oversight_agency,
        sac.submitted_by_id
    from
        public.audit_singleauditchecklist sac
    where
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    order by sac.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.tribal_access AS
    SELECT
        uup.email,
        up.slug as permission
    FROM
        users_userpermission uup,
        users_permission up
    WHERE
        (uup.permission_id = up.id)
        AND (up.slug = 'read-tribal')
        AND admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY uup.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.admin_api_events AS
    SELECT
        ae.timestamp,
        ae.api_key_uuid,
        ae.event,
        ae.event_data
    FROM
        public.support_adminapievent ae
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY ae.id
;



--------------------------------------------------------------------------
-- RAW CENSUS HISTORICAL TABLES

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecauditfindings AS
    SELECT
        eaf."ELECAUDITFINDINGSID", 
        eaf."ELECAUDITSID",
        eaf."AUDITYEAR",
        eaf."DBKEY",
        eaf."REPORTID",
        eaf."VERSION",
        eaf."QCOSTS",
        eaf."OTHERFINDINGS",
        eaf."SIGNIFICANTDEFICIENCY",
        eaf."MATERIALWEAKNESS",
        eaf."OTHERNONCOMPLIANCE",
        eaf."TYPEREQUIREMENT",
        eaf."FINDINGREFNUMS",
        eaf."MODIFIEDOPINION",
        eaf."REPEATFINDING",
        eaf."PRIORFINDINGREFNUMS"
    FROM 
        public.census_historical_migration_elecauditfindings eaf
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY eaf.id
;    

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecauditheader_ims AS
    SELECT
        eahi."ID",
        eahi."ID2",
        eahi."DBKEY",
        eahi."AUDITYEAR",
        eahi."TYPEAUDIT_CODE",
        eahi."SUPPRESSION_CODE",
        eahi."REPORTID",
        eahi."VERSION",
        eahi."IMAGE_EXISTS"
    FROM
        public.census_historical_migration_elecauditheader_ims eahi
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        eahi.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecauditheader AS
    SELECT
        eah."ELECAUDITHEADERID",
        eah."ID",
        eah."AUDITYEAR",
        eah."DBKEY",
        eah."FYENDDATE",
        eah."AUDITTYPE",
        eah."PERIODCOVERED",
        eah."NUMBERMONTHS",
        eah."MULTIPLEEINS",
        eah."EIN",
        eah."EINSUBCODE",
        eah."MULTIPLEDUNS",
        eah."DUNS",
        eah."AUDITEENAME",
        eah."STREET1",
        eah."STREET2",
        eah."CITY",
        eah."STATE",
        eah."ZIPCODE",
        eah."AUDITEECONTACT",
        eah."AUDITEETITLE",
        eah."AUDITEEPHONE",
        eah."AUDITEEFAX",
        eah."AUDITEEEMAIL",
        eah."AUDITEEDATESIGNED",
        eah."AUDITEENAMETITLE",
        eah."CPAFIRMNAME",
        eah."CPASTREET1",
        eah."CPASTREET2",
        eah."CPACITY",
        eah."CPASTATE",
        eah."CPAZIPCODE",
        eah."CPACONTACT",
        eah."CPATITLE",
        eah."CPAPHONE",
        eah."CPAFAX",
        eah."CPAEMAIL",
        eah."CPADATESIGNED",
        eah."CPANAMETITLE",
        eah."COG_OVER",
        eah."COGAGENCY",
        eah."TYPEREPORT_FS",
        eah."REPORTABLECONDITION",
        eah."MATERIALWEAKNESS",
        eah."MATERIALNONCOMPLIANCE",
        eah."GOINGCONCERN",
        eah."TYPEREPORT_MP",
        eah."DOLLARTHRESHOLD",
        eah."LOWRISK",
        eah."REPORTREQUIRED",
        eah."TOTFEDEXPEND",
        eah."COPIES",
        eah."REPORTABLECONDITION_MP",
        eah."MATERIALWEAKNESS_MP",
        eah."QCOSTS",
        eah."CYFINDINGS",
        eah."PYSCHEDULE",
        eah."DUP_REPORTS",
        eah."COG_AGENCY",
        eah."OVERSIGHTAGENCY",
        eah."DATERECEIVED",
        eah."DATEFIREWALL",
        eah."PREVIOUSDATEFIREWALL",
        eah."FINDINGREFNUM",
        eah."TYPEOFENTITY",
        eah."IMAGE",
        eah."AGENCYCFDA",
        eah."INITIALDATE",
        eah."DATERECEIVEDOTHER",
        eah."MULTIPLE_CPAS",
        eah."AUDITEECERTIFYNAME",
        eah."AUDITEECERTIFYTITLE",
        eah."FACACCEPTEDDATE",
        eah."AUDITOR_EIN",
        eah."SD_MATERIALWEAKNESS",
        eah."SD_MATERIALWEAKNESS_MP",
        eah."SIGNIFICANTDEFICIENCY",
        eah."SIGNIFICANTDEFICIENCY_MP",
        eah."SP_FRAMEWORK",
        eah."SP_FRAMEWORK_REQUIRED",
        eah."TYPEREPORT_SP_FRAMEWORK",
        eah."SUPPRESSION_CODE",
        eah."ENTITY_TYPE",
        eah."TYPEAUDIT_CODE",
        eah."OPEID",
        eah."DATETOED",
        eah."DATEFINISHED",
        eah."TYPEFINDING",
        eah."TYPEFUNDING",
        eah."FYSTARTDATE",
        eah."CPAFOREIGN",
        eah."UEI",
        eah."MULTIPLEUEIS",
        eah."CPACOUNTRY"
    FROM
        public.census_historical_migration_elecauditheader eah
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        eah.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecaudits AS
    SELECT
        ea."ELECAUDITSID",
        ea."ID",
        ea."AUDITYEAR",
        ea."DBKEY",
        ea."CFDASEQNUM",
        ea."CFDA",
        ea."FEDERALPROGRAMNAME",
        ea."AMOUNT",
        ea."MAJORPROGRAM",
        ea."TYPEREQUIREMENT",
        ea."QCOSTS2",
        ea."FINDINGS",
        ea."FINDINGREFNUMS",
        ea."RD",
        ea."DIRECT",
        ea."CFDA_PREFIX",
        ea."CFDA_EXT",
        ea."EIN",
        ea."CFDA2",
        ea."TYPEREPORT_MP",
        ea."TYPEREPORT_MP_OVERRIDE",
        ea."ARRA",
        ea."LOANS",
        ea."FINDINGSCOUNT",
        ea."LOANBALANCE",
        ea."PASSTHROUGHAMOUNT",
        ea."AWARDIDENTIFICATION",
        ea."CLUSTERNAME",
        ea."PASSTHROUGHAWARD",
        ea."STATECLUSTERNAME",
        ea."PROGRAMTOTAL",
        ea."CLUSTERTOTAL",
        ea."OTHERCLUSTERNAME",
        ea."CFDAPROGRAMNAME",
        ea."UEI",
        ea."MULTIPLEUEIS"
    FROM
        public.census_historical_migration_elecaudits ea
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        ea.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.eleccaptext AS
    SELECT
        ect."SEQ_NUMBER",
        ect."DBKEY",
        ect."AUDITYEAR",
        ect."FINDINGREFNUMS",
        ect."TEXT",
        ect."CHARTSTABLES",
        ect."REPORTID",
        ect."VERSION",
        ect."UEI",
        ect."MULTIPLEUEIS"
    FROM
        public.census_historical_migration_eleccaptext ect
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        ect.id
;


CREATE OR REPLACE VIEW admin_api_v2_0_0.eleccpas AS
    SELECT
        ecpa."ID",
        ecpa."AUDITYEAR",
        ecpa."DBKEY",
        ecpa."SEQNUM",
        ecpa."VERSION",
        ecpa."CPAFIRMNAME",
        ecpa."CPASTREET1",
        ecpa."CPACITY",
        ecpa."CPASTATE",
        ecpa."CPAZIPCODE",
        ecpa."CPACONTACT",
        ecpa."CPATITLE",
        ecpa."CPAPHONE",
        ecpa."CPAFAX",
        ecpa."CPAEMAIL",
        ecpa."CPAEIN"
    FROM
        public.census_historical_migration_eleccpas ecpa
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        ecpa.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.eleceins as
    SELECT
        eein."ID",
        eein."AUDITYEAR",
        eein."DBKEY",
        eein."EIN",
        eein."EINSEQNUM",
        eein."DUNS",
        eein."DUNSEQNUM"
    FROM
        public.census_historical_migration_eleceins eein
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        eein.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecfindingstext AS
    SELECT
        eft."SEQ_NUMBER",
        eft."DBKEY",
        eft."AUDITYEAR",
        eft."FINDINGREFNUMS",
        eft."TEXT",
        eft."CHARTSTABLES",
        eft."REPORTID",
        eft."VERSION",
        eft."UEI",
        eft."MULTIPLEUEIS"
    FROM
        public.census_historical_migration_elecfindingstext eft
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        eft.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecnotes AS
    SELECT
        en."ID",
        en."REPORTID",
        en."VERSION",
        en."DBKEY",
        en."AUDITYEAR",
        en."SEQ_NUMBER",
        en."TYPE_ID",
        en."NOTE_INDEX",
        en."TITLE",
        en."CONTENT",
        en."UEI",
        en."MULTIPLEUEIS"
    FROM
        public.census_historical_migration_elecnotes en
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        en.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecpassthrough AS
    SELECT
        ep."ID",
        ep."AUDITYEAR",
        ep."DBKEY",
        ep."ELECAUDITSID",
        ep."PASSTHROUGHNAME",
        ep."PASSTHROUGHID"
    FROM
        public.census_historical_migration_elecpassthrough ep
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        ep.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecrpt_revisions AS
    SELECT
        err."ELECRPTREVISIONID",
        err."REPORTID",
        err."VERSION",
        err."DBKEY",
        err."AUDITYEAR",
        err."GENINFO",
        err."GENINFO_EXPLAIN",
        err."FEDERALAWARDS",
        err."FEDERALAWARDS_EXPLAIN",
        err."NOTESTOSEFA",
        err."NOTESTOSEFA_EXPLAIN",
        err."AUDITINFO",
        err."AUDITINFO_EXPLAIN",
        err."FINDINGS",
        err."FINDINGS_EXPLAIN",
        err."FINDINGSTEXT",
        err."FINDINGSTEXT_EXPLAIN",
        err."CAP",
        err."CAP_EXPLAIN",
        err."OTHER",
        err."OTHER_EXPLAIN"
    FROM
        public.census_historical_migration_elecrpt_revisions err
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        err.id
;

CREATE OR REPLACE VIEW admin_api_v2_0_0.elecueis AS
    SELECT
        euei."UEISID",
        euei."REPORTID",
        euei."VERSION",
        euei."DBKEY",
        euei."AUDITYEAR",
        euei."UEI",
        euei."SEQNUM"
    FROM
        public.census_historical_migration_elecueis euei
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        euei.id
; 

CREATE OR REPLACE VIEW admin_api_v2_0_0.federalagencylookup AS
    SELECT
        fal."ID",
        fal."CFDAPREFIX",
        fal."NAME",
        fal."ACRONYM",
        fal."STARTEXT",
        fal."ENDEXT"
    FROM
        public.census_historical_migration_federalagencylookup fal
    WHERE
        admin_api_v2_0_0_functions.has_admin_data_access('READ')
    ORDER BY
        fal.id
; 

commit;

notify pgrst,
       'reload schema';
