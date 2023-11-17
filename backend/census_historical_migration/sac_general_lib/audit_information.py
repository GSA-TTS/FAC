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

DOLLAR_THRESHOLD = 750000

mappings = [
    FormFieldMap(
        "dollar_threshold", None, FormFieldInDissem, DOLLAR_THRESHOLD, int
    ),  # FIXME: There is no in_db mapping ?
    FormFieldMap(
        "gaap_results", None, FormFieldInDissem, [], list
    ),  # FIXME: There is no in_db mapping?
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
    FormFieldMap(
        "is_low_risk_auditee", None, FormFieldInDissem, False, bool
    ),  # FIXME: There is no in_db mapping?
    FormFieldMap(
        "agencies", None, "agencies_with_prior_findings", [], list
    ),  # FIXME: There is no in_db mapping?
]


def _get_agency_prefixes(dbkey):
    agencies = {}
    cfdas = Cfda.select().where(Cfda.dbkey == dbkey)
    cfda: Cfda
    for cfda in cfdas:
        agencies[int((cfda.cfda).split(".")[0])] = 1
    return agencies.keys()


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


def _boolean_field(audit_info, field_name):
    audit_info[field_name] = audit_info.get(field_name, "N") == "Y"
    return audit_info


def _xform_agencies(audit_info):
    new_audit_info = audit_info.copy()
    # Apply transformation to each key
    transformed_agencies = [
        str(i) if len(str(i)) > 1 else f"0{str(i)}" for i in audit_info.get("agencies")
    ]

    new_audit_info["agencies"] = transformed_agencies
    return new_audit_info


def _xform_aicpa_audit_guide_included(audit_info):
    return _boolean_field(audit_info, "is_aicpa_audit_guide_included")


def _xform_going_concern_included(audit_info):
    return _boolean_field(audit_info, "is_going_concern_included")


def _xform_internal_control_deficiency_disclosed(audit_info):
    return _boolean_field(audit_info, "is_internal_control_deficiency_disclosed")


def _xform_internal_control_material_weakness_disclosed(audit_info):
    return _boolean_field(audit_info, "is_internal_control_material_weakness_disclosed")


def _xform_material_noncompliance_disclosed(audit_info):
    return _boolean_field(audit_info, "is_material_noncompliance_disclosed")


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
        _xform_aicpa_audit_guide_included,
        _xform_going_concern_included,
        _xform_internal_control_deficiency_disclosed,
        _xform_internal_control_material_weakness_disclosed,
        _xform_material_noncompliance_disclosed,
    ]

    # Apply transformations
    for transform in transformations:
        audit_information = transform(audit_information)

    # Validate against the schema
    audit.validators.validate_audit_information_json(audit_information)

    return audit_information
