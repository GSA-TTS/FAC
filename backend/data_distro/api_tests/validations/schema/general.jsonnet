local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer,
    dollar_threshold: Types.integer,
    special_framework_required: Types.StringOrNull,
    going_concern: Types.boolean,
    material_weakness: Types.boolean,
    material_noncompliance: Types.boolean,
    dup_reports: Types.boolean,
    low_risk: Types.boolean,
    condition_or_deficiency_major_program: Types.boolean,
    material_weakness_major_program: Types.boolean,
    questioned_costs: Types.boolean,
    current_or_former_findings: Types.boolean,
    prior_year_schedule: Types.BooleanOrNull,
    report_required: Types.BooleanOrNull,
    total_fed_expenditures: Types.integer,
    cognizant_agency: Types.StringOrNull,
    oversight_agency: Types.integer,
    entity_type: Types.string, // FIXME: ENUM?
    period_covered: Types.string, // FIXME: REGEX
    special_framework: Types.StringOrNull,
    type_of_entity: Types.string, // FIXME?
    fy_start_date: Types.StringOrNull, // REGEX
    fy_end_date: Types.string, // REGEX
    auditee_date_signed: Types.string,
    cpa_date_signed: Types.string,
    initial_date_received: Types.StringOrNull,
    form_date_received: Types.StringOrNull,
    component_date_received: Types.StringOrNull,
    completed_date: Types.StringOrNull,
    previous_completed_on: Types.StringOrNull,
    fac_accepted_date: Types.string, // All dates need a regex
    number_months: Types.IntegerOrNull,
    audit_type: Types.string, // REGEX
    type_report_financial_statements: Types.string, // REGEX
    type_report_special_purpose_framework: Types.StringOrNull,
    type_report_major_program: Types.string, // REGEX
    dbkey: Types.DBKEY,
    audit_year: Types.string, //REGEX
    date_published: Types.string, // REGEX
    previous_date_published: Types.StringOrNull, // REGEX
    cognizant_agency_over: Types.string, //REGEX or ENUM
    revision_id: Types.IntegerOrNull,
    create_date: Types.string, // REGEX
    data_source: Types.string, // ENUM
    is_public: Types.boolean, // Should always be true in these tests
    modified_date: Types.string, //'2023-03-27T18:30:55.069944+00:00'
    auditee_id: Types.integer,
    reportable_condition: Types.boolean,
    significant_deficiency: Types.BooleanOrNull,
    primary_auditor_id: Types.integer,
    pdf_urls: {
      oneOf: [ 
        Types.NULL,
        { type: "array", items: {type: ["string"]}},
      ]
    },
    auditee_name: Types.string,
    cpa_firm_name: Types.string,
  },
}
