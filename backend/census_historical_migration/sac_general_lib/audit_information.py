from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
    CensusCfda22 as Cfda,
    CensusFindings22 as Finding,
)
from census_historical_migration.base_field_maps import FormFieldMap, FormFieldInDissem
from census_historical_migration.sac_general_lib.utils import (
    _create_json_from_db_object,
)
import audit.validators
from django.conf import settings


mappings = [
    FormFieldMap(
        "dollar_threshold",
        "dollarthreshold",
        FormFieldInDissem,
        settings.DOLLAR_THRESHOLD,
        int,
    ),
    FormFieldMap("gaap_results", "typereport_fs", FormFieldInDissem, [], list),
    FormFieldMap(
        "is_going_concern_included", "goingconcern", FormFieldInDissem, None, bool
    ),
    FormFieldMap(
        "is_internal_control_deficiency_disclosed",
        "materialweakness",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap(
        "is_internal_control_material_weakness_disclosed",
        "materialweakness_mp",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap(
        "is_material_noncompliance_disclosed",
        "materialnoncompliance",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap(
        "is_aicpa_audit_guide_included",
        "reportablecondition",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap("is_low_risk_auditee", "lowrisk", FormFieldInDissem, False, bool),
    FormFieldMap("agencies", "pyschedule", "agencies_with_prior_findings", [], list),
]


def _get_agency_prefixes(dbkey):
    agencies = set()
    cfdas = Cfda.select().where(Cfda.dbkey == dbkey)

    for cfda in cfdas:
        agency_prefix = int(cfda.cfda.split(".")[0])
        agencies.add(agency_prefix)

    return agencies


def _get_gaap_results(dbkey):
    findings = Finding.select().where(Finding.dbkey == dbkey)
    gaap_results = {}
    # FIXME: How do we retrieve gaap_results from the historic data? I could not find corresponding fields in Census tables.
    for finding in findings:
        if finding.modifiedopinion == "Y":
            gaap_results["unmodified_opinion"] = 1
        if finding.materialweakness == "Y":
            gaap_results["adverse_opinion"] = 1
        if finding.significantdeficiency == "Y":
            gaap_results["disclaimer_of_opinion"] = 1
    return gaap_results.keys()


def _xform_agencies(audit_info):
    new_audit_info = audit_info.copy()
    # Apply transformation to each key
    transformed_agencies = [
        str(i) if len(str(i)) > 1 else f"0{str(i)}" for i in audit_info.get("agencies")
    ]

    new_audit_info["agencies"] = transformed_agencies
    return new_audit_info


def _build_initial_audit_information(dbkey):
    gaap_results = _get_gaap_results(dbkey)
    agencies_prefixes = _get_agency_prefixes(dbkey)
    gobj = Gen.select().where(Gen.dbkey == dbkey).first()
    audit_information = _create_json_from_db_object(gobj, mappings)
    audit_information["gaap_results"] = list(gaap_results)
    audit_information["agencies"] = list(agencies_prefixes)
    return audit_information


def _audit_information(dbkey):
    audit_information = _build_initial_audit_information(dbkey)

    # List of transformation functions
    transformations = [
        _xform_agencies,
    ]

    # Apply transformations
    for transform in transformations:
        audit_information = transform(audit_information)

    # Validate against the schema
    audit.validators.validate_audit_information_json(audit_information)

    return audit_information
