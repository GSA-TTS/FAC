import 'cypress-file-upload';
import { testValidAccess } from '../support/check-access.js';
import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';
import { testValidGeneralInfo } from '../support/general-info.js';
import { testReportIdNotFound } from '../support/dissemination-table.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import {
  testWorkbookAdditionalEINs,
  testWorkbookFederalAwards,
} from '../support/workbook-uploads.js';

describe('Additional EINs page', () => {
  before(() => {
    cy.session('login-session', () => {
      cy.visit('/');
      cy.login();
    });
  });

  it('Additional EINs uploads successfully', () => {
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

    cy.get(".usa-link").contains("Additional EINs").click();
    testWorkbookAdditionalEINs(false);
  });

  it('Displays message if file has already been uploaded', () => {
    testFileUploadMsg('Edit the Additional EINs');
  });
});
