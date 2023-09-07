const { spawn } = require('node:child_process');

const pa11y = require('pa11y');
const fs = require('fs');
const glob = require('glob');
const path = require('path');

const urls = [
  'http://localhost:8000/',
  'http://localhost:8000/report_submission/eligibility',
  'http://localhost:8000/report_submission/auditeeinfo',
  'http://localhost:8000/report_submission/accessandsubmission',
  'http://localhost:8000/audit',
];

const config = {
  runners: ['axe', 'htmlcs'],
  hideElements:
    '.pa11y-ignore, .usa-select, .usa-step-indicator__segment-label, .is-hidden, #upload-worksheet, .usa-file-input__instructions, #my-submissions',
  standard: 'WCAG2AA',
  // FIXME: temporarily ignoring contrast issues until pa11y fixes https://github.com/pa11y/pa11y/issues/633 or we find a workaround
  ignore: ['color-contrast'],
};

scanPages(urls);

async function scanPages(pages) {
  try {
    const results = await Promise.all(
      urls.map((u) => {
        return pa11y(u, config);
      })
    );
    let totalIssues = 0;
    results.forEach((r) => {
      if (r.issues.length > 0) {
        let issueCount = 0;
        r.issues.forEach((i) => {
          issueCount += 1;
          console.log(
            `
====
PAGE:    ${r.pageUrl}
CODE:    ${i.code}
MESSAGE: ${i.message}
CONTEXT: ${i.context}
----`
          );
        });
        totalIssues += issueCount;
        console.log(`\n❌ pa11y found ${issueCount} issues on ${r.pageUrl}\n`);
      } else {
        console.log(`🎉 No issues found on ${r.pageUrl}!`);
      }
    });
    if (totalIssues > 0) {
      console.log(`❌ pa11y found ${totalIssues} total issues.`);
      process.exit(1);
    } else {
      console.log(`🎉 pa11y found 0 issues.`);
      process.exit(0);
    }
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}
