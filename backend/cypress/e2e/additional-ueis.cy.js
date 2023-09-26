import 'cypress-file-upload';
import { testCrossValidation } from '../support/cross-validation.js';
import { testLoginGovLogin } from '../support/login-gov.js';
//import { testLogoutGov } from '../support/logout-gov.js';
import { testValidAccess } from '../support/check-access.js';
import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';
import { testValidGeneralInfo } from '../support/general-info.js';
import { testReportIdFound, testReportIdNotFound } from '../support/dissemination-table.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';

import {
    testWorkbookAdditionalUEIs,
  testWorkbookFederalAwards,
} from '../support/workbook-uploads.js';

const LOGIN_TEST_EMAIL_AUDITEE = Cypress.env('LOGIN_TEST_EMAIL_AUDITEE');
const LOGIN_TEST_PASSWORD_AUDITEE = Cypress.env('LOGIN_TEST_PASSWORD_AUDITEE');
const LOGIN_TEST_OTP_SECRET_AUDITEE = Cypress.env('LOGIN_TEST_OTP_SECRET_AUDITEE');

describe('Additional UEIs page', () => {
  before(() => {
    cy.session('login-session', () => {
      cy.visit('/');
      cy.login();
    });
  });

  it('Additional UEIs uploads successfully', () => {
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

    cy.get(".usa-link").contains("Additional UEIs").click();
    testWorkbookAdditionalUEIs(false);
  });

  it('Displays message if file has already been uploaded', () => {
    testFileUploadMsg('Edit the Additional UEIs');
  });

});