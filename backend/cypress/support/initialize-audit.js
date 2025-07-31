import { testValidAccess } from './check-access.js'
import { testValidEligibility } from './check-eligibility.js';
import { testValidAuditeeInfo } from './auditee-info.js';
import { testValidGeneralInfo } from './general-info.js';
import { testWithUnprivilegedKey } from './dissemination-table.js';

export function testInitializeAudit(isTribal = false) {
  // Completes the eligibility screen
  testValidEligibility(isTribal);

  // Now the auditee info screen
  testValidAuditeeInfo();

  // Now the accessandsubmission screen
  testValidAccess();

  // Report should not yet be in the dissemination table
  cy.url().then(url => {
    const reportId = url.split('/').pop();
    // testReportIdNotFoundWithTribalAccess(reportId);
    // testReportIdNotFoundWithoutTribalAccess(reportId);
    testWithUnprivilegedKey(reportId, 'general', 0);
  });

  // Fill out the general info form
  testValidGeneralInfo();
};
