local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local AuditorCertification = Types.object {
  additionalProperties: false,
  properties: {
    auditor_certification: Types.object {
      description: 'Auditor certification (required checkboxes)',
      properties: {
        is_OMB_limited: Types.boolean,
        is_auditee_responsible: Types.boolean,
        has_used_auditors_report: Types.boolean,
        has_no_auditee_procedures: Types.boolean,
        is_FAC_releasable: Types.boolean,
      },
      required: [
        'is_OMB_limited',
        'is_auditee_responsible',
        'has_used_auditors_report',
        'has_no_auditee_procedures',
        'is_FAC_releasable',
      ],
    },
    auditor_signature: Types.object {
      description: 'Auditor signature and title',
      properties: {
        auditor_name: Types.string,
        auditor_title: Types.string,
        auditor_certification_date_signed: Base.Compound.Date,
      },
      required: ['auditor_name', 'auditor_title'],
    },
  },
  title: 'AuditorCertification',
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    AuditorCertification: AuditorCertification,
  },
  version: 20230802,
};

AuditorCertification
