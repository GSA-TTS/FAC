module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:8000/',
        'http://localhost:8000/report_submission/eligibility',
        'http://localhost:8000/report_submission/auditeeinfo',
        'http://localhost:8000/report_submission/accessandsubmission',
        'http://localhost:8000/audit',
      ],
    },
    assert: {
      assertions: {
        "categories:accessibility": ["error", {"minScore": .98}]
      }
    }
  },
};
