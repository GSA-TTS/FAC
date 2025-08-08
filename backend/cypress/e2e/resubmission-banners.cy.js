import { testInitializeAudit } from '../support/initialize-audit.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import { testLogoutGov } from '../support/logout-gov.js';

/*
 * To run these tests, see the notes below in the "Valid report_ids" block
 * about replacing the previous_report_ids with report_ids you have locally in
 * audit_singleauditchecklist. Submissions generated from full-submissions
 * can't be used because they're already resubmissions of each other, since
 * they share the same date/UEI.
 */

const LOGIN_TEST_EMAIL_AUDITEE = Cypress.env('LOGIN_TEST_EMAIL_AUDITEE');
const LOGIN_TEST_PASSWORD_AUDITEE = Cypress.env('LOGIN_TEST_PASSWORD_AUDITEE');
const LOGIN_TEST_OTP_SECRET_AUDITEE = Cypress.env('LOGIN_TEST_OTP_SECRET_AUDITEE');

// Helper for testing tribal resubmissions
function testTribal(previous_report_id, was_private) {
  if (previous_report_id === 'REPLACE-ME') {
    throw new Error("You must replace 'REPLACE-ME' with a valid previous_report_id");
  }

  cy.get('[id=report_id]').type(previous_report_id);
  cy.get('[id=continue]').click();
  cy.url().should('include', '/report_submission/eligibility/');
  testInitializeAudit(false, true);
  cy.url().should('include', '/audit/submission-progress/');

  cy.url().then(url => {
    const reportId = url.split('/').pop();
    testLogoutGov();
    testLoginGovLogin(
      LOGIN_TEST_EMAIL_AUDITEE,
      LOGIN_TEST_PASSWORD_AUDITEE,
      LOGIN_TEST_OTP_SECRET_AUDITEE
    );

    cy.visit(`/audit/submission-progress/${reportId}`);
    cy.get(".usa-link").contains("Tribal data release").click();
    cy.get('[id=tribal-consent-banner]').contains(
      `Note: The previous submission of this audit opted ${was_private ? 'not ' : ''}to authorize the FAC to make the reporting package publicly available.`
    );
    cy.get(`[id=is_tribal_information_authorized_to_be_public-${was_private ? 'no' : 'yes'}]`).should('be.checked');
  });
}

describe('Resubmission banners', () => {
  beforeEach(() => {
    cy.visit('/');
    testLoginGovLogin();
    cy.visit('/audit/resubmission-start');
  });

  afterEach(() => {
    testLogoutGov();
  });

  it('Checklist banner', () => {
    // Replace with a report_id of a normal audit
    const previous_report_id = 'REPLACE-ME'
    cy.get('[id=report_id]').type(previous_report_id);
    cy.get('[id=continue]').click();
    cy.url().should('include', '/report_submission/eligibility/');
    testInitializeAudit(false, true);
    cy.url().should('include', '/audit/submission-progress/');
    cy.get('[id=resubmission-banner]').contains(`Resubmission of ${previous_report_id} in progress.`);
  });

  // Replace with a report_id of a public, tribal audit:
  // tribal_data_consent.is_tribal_information_authorized_to_be_public = true
  it.only('Tribal public banner', () => {
    const previous_report_id = 'REPLACE-ME'
    testTribal(previous_report_id, false);
  });

  // Replace with a report_id of a non-public, tribal audit:
  // tribal_data_consent->is_tribal_information_authorized_to_be_public = false
  it('Tribal non-public banner', () => {
    const previous_report_id = 'REPLACE-ME'
    testTribal(previous_report_id, true);
  });
});
