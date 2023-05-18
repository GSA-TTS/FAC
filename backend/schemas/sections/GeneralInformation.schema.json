{
   "$defs": {
      "AuditPeriod": {
         "description": "",
         "enum": [
            "annual",
            "biennial",
            "other"
         ],
         "title": "AuditPeriod",
         "type": "string"
      },
      "EIN": {
         "pattern": "^[0-9]{9}$",
         "type": [
            "string",
            "null"
         ]
      },
      "Phone": {
         "pattern": "^^(\\+0?1\\s)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}$",
         "type": "string"
      },
      "State": {
         "enum": [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY"
         ],
         "title": "State",
         "type": "string"
      },
      "UEI": {
         "pattern": "^$|^[a-hj-np-zA-HJ-NP-Z1-9][a-hj-np-zA-HJ-NP-Z0-9]{11}$",
         "type": [
            "string",
            "null"
         ]
      },
      "UserProvidedOrganizationType": {
         "enum": [
            "higher-ed",
            "local",
            "non-profit",
            "none",
            "state",
            "tribal",
            "unknown"
         ],
         "type": "string"
      },
      "Zip": {
         "pattern": "^[0-9]{5}(?:-[0-9]{4})?$",
         "type": "string"
      }
   },
   "$id": "http://example.org/generalinformation",
   "$schema": "http://json-schema.org/draft/2019-09/schema#",
   "additionalProperties": false,
   "metamodel_version": "1.7.0",
   "properties": {
      "audit_period_covered": {
         "$ref": "#/$defs/AuditPeriod"
      },
      "auditee_address_line_1": {
         "maxLength": 100,
         "type": "string"
      },
      "auditee_city": {
         "maxLength": 100,
         "type": "string"
      },
      "auditee_contact_name": {
         "maxLength": 100,
         "type": "string"
      },
      "auditee_contact_title": {
         "maxLength": 100,
         "type": "string"
      },
      "auditee_email": {
         "format": "email",
         "type": "string"
      },
      "auditee_fiscal_period_end": {
         "format": "date",
         "type": "string"
      },
      "auditee_fiscal_period_start": {
         "format": "date",
         "type": "string"
      },
      "auditee_name": {
         "type": [
            "string",
            "null"
         ]
      },
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
      "auditor_address_line_1": {
         "maxLength": 100,
         "type": "string"
      },
      "auditor_city": {
         "maxLength": 100,
         "type": "string"
      },
      "auditor_contact_name": {
         "maxLength": 100,
         "type": "string"
      },
      "auditor_contact_title": {
         "maxLength": 100,
         "type": "string"
      },
      "auditor_country": {
         "maxLength": 100,
         "type": "string"
      },
      "auditor_ein": {
         "$ref": "#/$defs/EIN"
      },
      "auditor_ein_not_an_ssn_attestation": {
         "type": [
            "boolean",
            "null"
         ]
      },
      "auditor_email": {
         "format": "email",
         "type": "string"
      },
      "auditor_firm_name": {
         "type": "string"
      },
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
      "ein_not_an_ssn_attestation": {
         "type": [
            "boolean",
            "null"
         ]
      },
      "is_usa_based": {
         "type": "boolean"
      },
      "met_spending_threshold": {
         "type": "boolean"
      },
      "multiple_eins_covered": {
         "type": [
            "boolean",
            "null"
         ]
      },
      "multiple_ueis_covered": {
         "type": [
            "boolean",
            "null"
         ]
      },
      "user_provided_organization_type": {
         "$ref": "#/$defs/UserProvidedOrganizationType"
      }
   },
   "required": [ ],
   "title": "GeneralInformation",
   "type": "object",
   "version": null
}
