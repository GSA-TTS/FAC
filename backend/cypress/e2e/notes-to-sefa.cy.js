import 'cypress-file-upload';
import { testValidAccess } from '../support/check-access.js';
import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';
import { testValidGeneralInfo } from '../support/general-info.js';
import { testReportIdNotFound } from '../support/dissemination-table.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import {
  testWorkbookFederalAwards,
  testWorkbookNotesToSEFA
} from '../support/workbook-uploads.js';

describe('Notes to SEFA page', () => {
  before(() => {
    cy.session('login-session', () => {
      cy.visit('/');
      cy.login();
    });
  });

  it('Notes to SEFA uploads successfully', () => {
    cy.visit('/');

    cy.url().should('include', '/');

    cy.get('label[for=check-start-new-submission]').click();

    cy.get('.usa-button').contains('Accept and start').click();

    cy.url().should('match', /\/report_submission\/eligibility\/$/);

    testValidEligibility();

    testValidAuditeeInfo();

    testValidAccess();

    // Report should not yet be in the dissemination table
    cy.url().then(url => {
      const reportId = url.split('/').pop();
      testReportIdNotFound(reportId);
    });

    testValidGeneralInfo();

    cy.get(".usa-link").contains("Federal Awards").click();
    testWorkbookFederalAwards(false);

    cy.get(".usa-link").contains("Notes to SEFA").click();
    testWorkbookNotesToSEFA(false);
  });

  it('Displays message if file has already been uploaded', () => {
    testFileUploadMsg('Edit the Notes to SEFA');
  });
});
