local FormTypes = {
  YMD: 'YMD',
  Checklist: 'checklist',
  RadioGroup: 'radiogroup',
  RadioGroupOther: 'radiougroupother',
};

{
  title: 'SF-SAC',
  parts: {
    _1: {
      title: 'General Information',
      parts: {
        _1: {
          title: 'Fiscal Period',
          parts: {
            a: {
              title: 'Start date',
              type: FormTypes.YMD,
            },
            b: {
              title: 'End date',
              type: FormTypes.YMD,
            },
          },
        },
        _2: {
          title: 'Type of Uniform Guidance audit',
          type: FormTypes.RadioGroup,
          // These values may need additional metadata associated with them?
          values: [
            'Single audit',
            'Program-specific audit',
            'Alternative Compliance Examination Engagement (ACEE)',
          ],
        },
        _3: {
          parts: {
            title: 'Audit period covered',
            type: FormTypes.RadioGroupOther,
            values: [
              'Annual',
              'Biennial',
              'Other',
            ],

          },
        },
      },
    },
  },
}
