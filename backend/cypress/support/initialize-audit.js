import { testValidAccess } from './check-access.js';
import { testValidEligibility } from './check-eligibility.js';
import { testValidAuditeeInfo } from './auditee-info.js';
import { testValidGeneralInfo } from './general-info.js';
import { testReportIdNotFoundWithTribalAccess, testReportIdNotFoundWithoutTribalAccess } from './dissemination-table.js';

export function testInitializeAudit(isTribal=false) {
  // Check the terms and conditions link and click "Accept and start..."
  cy.get('label[for=check-start-new-submission]').click();
  cy.get('.usa-button').contains('Accept and start').click();
  cy.url().should('match', /\/report_submission\/eligibility\/$/);

  // Completes the eligibility screen
  testValidEligibility(isTribal);

  // Now the auditee info screen
  testValidAuditeeInfo();

  // Now the accessandsubmission screen
  testValidAccess();

  // Report should not yet be in the dissemination table
  cy.url().then(url => {
    const reportId = url.split('/').pop();
    testReportIdNotFoundWithTribalAccess(reportId);
    testReportIdNotFoundWithoutTribalAccess(reportId);
  });

  // Fill out the general info form
  testValidGeneralInfo();
}
