local Base = import 'Base.libsonnet';
local Func = import 'Functions.libsonnet';
local Types = Base.Types;

{
   "$defs": {
      "AuditPeriod": Base.Enum.AuditPeriod,
      "EIN": Types.string_or_null {
         "pattern": "^[0-9]{9}$",
      },
      "Phone": Types.string {
         "pattern": "^^(\\+0?1\\s)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}$",
      },
      "State": Base.Enum.UnitedStatesStateAbbr {
         "title": "State",
      },
      "UEI": Types.string_or_null {
         "pattern": "^$|^[a-hj-np-zA-HJ-NP-Z1-9][a-hj-np-zA-HJ-NP-Z0-9]{11}$",
      },
      "UserProvidedOrganizationType": Base.Enum.OrganizationType,
      "Zip": Types.string {
         "pattern": "^[0-9]{5}(?:-[0-9]{4})?$",
      }
   },
   "$id": "http://example.org/generalinformation",
   "$schema": "http://json-schema.org/draft/2019-09/schema#",
   "additionalProperties": false,
   "metamodel_version": "1.7.0",
   "properties": {
      "audit_type": Base.Enum.AuditType,
      "audit_period_covered": {
         "$ref": "#/$defs/AuditPeriod"
      },
      "auditee_address_line_1": Types.string {
         "maxLength": 100,
      },
      "auditee_city": Types.string {
         "maxLength": 100,
      },
      "auditee_contact_name": Types.string {
         "maxLength": 100,
      },
      "auditee_contact_title": Types.string {
         "maxLength": 100,
      },
      "auditee_email": Types.string {
         "format": "email",
      },
      "auditee_fiscal_period_end": Types.string {
         "format": "date",
      },
      "auditee_fiscal_period_start": Types.string {
         "format": "date",
      },
      "auditee_name": Types.string_or_null {},
      "auditee_phone": {
         "$ref": "#/$defs/Phone"
      },
      "auditee_state": {
         "$ref": "#/$defs/State"
      },
      "auditee_uei": {
         "$ref": "#/$defs/UEI"
      },
      "auditee_zip": {
         "$ref": "#/$defs/Zip"
      },
      "auditor_address_line_1": Types.string {
         "maxLength": 100,
      },
      "auditor_city": Types.string {
         "maxLength": 100,
      },
      "auditor_contact_name": Types.string {
         "maxLength": 100,
      },
      "auditor_contact_title": Types.string {
         "maxLength": 100,
      },
      "auditor_country": Types.string {
         "maxLength": 100,
      },
      "auditor_ein": {
         "$ref": "#/$defs/EIN"
      },
      "auditor_ein_not_an_ssn_attestation": Types.boolean_or_null,
      "auditor_email": Types.string {
         "format": "email",
      },
      "auditor_firm_name": Types.string,
      "auditor_phone": {
         "$ref": "#/$defs/Phone"
      },
      "auditor_state": {
         "$ref": "#/$defs/State"
      },
      "auditor_zip": {
         "$ref": "#/$defs/Zip"
      },
      "ein": {
         "$ref": "#/$defs/EIN"
      },
      "ein_not_an_ssn_attestation": Types.boolean_or_null,
      "is_usa_based": Types.boolean,
      "met_spending_threshold": Types.boolean,
      "multiple_eins_covered": Types.boolean_or_null,
      "multiple_ueis_covered": Types.boolean_or_null,
      "user_provided_organization_type": {
         "$ref": "#/$defs/UserProvidedOrganizationType"
      }
   },
   "required": [ ],
   "title": "GeneralInformation",
   "type": "object",
   "version": null
}
