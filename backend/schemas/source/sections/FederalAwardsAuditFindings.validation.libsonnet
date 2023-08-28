local Base = import '../base/Base.libsonnet';

local Validations = {
  Combinations:[
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.Y,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.Y,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.Y,
          },
          significant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.Y,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significant_deficiency: {
            const: Base.Const.Y,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.Y,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.Y,
          },
          material_weakness: {
            const: Base.Const.Y,
          },
          significant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.Y,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significant_deficiency: {
            const: Base.Const.Y,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.Y,
          },
          significant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significant_deficiency: {
            const: Base.Const.Y,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.Y,
          },
        },
      },
    },                  
  ],
  PriorReferences: [
    {
      allOf: [
        {
          "if": {
            properties: {
              repeat_prior_reference: {
                const: Base.Const.Y
              }
            }
          },
          "then": {
            properties: {
              "prior_references": Base.Compound.PriorReferences
            }
          }
        },
        {
          not: {
            properties: {
              repeat_prior_reference: {
                const: Base.Const.N
              }
            }
          }
        }
      ]
    },
    {
      allOf: [
        {
          "if": {
            properties: {
              repeat_prior_reference: {
                const: Base.Const.N
              }
            }
          },
          "then": {
            properties: {
              prior_references: {
                const: Base.Const.NA
              }
            }
          }
        },
        {
          not: {
            properties: {
              repeat_prior_reference: {
                const: Base.Const.Y
              }
            }
          }
        }
      ]
    }
  ],   
};

{
  Validations: Validations,
}