local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local AuditeeCertification = Types.object {
  additionalProperties: false,
  properties: {
    auditee_certification: Types.object {
      description: 'Auditee certification (required checkboxes)',
      properties: {
        has_no_PII: Types.boolean,
        has_no_BII: Types.boolean,
        meets_2CFR_specifications: Types.boolean,
        is_2CFR_compliant: Types.boolean,
        is_complete_and_accurate: Types.boolean,
        has_engaged_auditor: Types.boolean,
        is_issued_and_signed: Types.boolean,
        is_FAC_releasable: Types.boolean,
      },
      required: [
        'has_no_PII',
        'has_no_BII',
        'meets_2CFR_specifications',
        'is_2CFR_compliant',
        'is_complete_and_accurate',
        'has_engaged_auditor',
        'is_issued_and_signed',
        'is_FAC_releasable',
      ],
    },
    auditee_signature: Types.object {
      description: 'Auditee signature and title',
      properties: {
        auditee_name: Types.string {
          minimum: 1,
        },
        auditee_title: Types.string {
          minimum: 1,
        },
        auditee_certification_date_signed: Base.Compound.Date,
      },
      required: ['auditee_name', 'auditee_title','auditee_certification_date_signed'],
    },
  },
  required: ['auditee_certification', 'auditee_signature'],
  title: 'AuditeeCertification',
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    AuditeeCertification: AuditeeCertification,
  },
  version: 20230802,
};

AuditeeCertification
