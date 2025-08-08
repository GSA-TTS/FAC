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
    cy.get(`[id=is_tribal_information_authorized_to_be_public-${was_private ? 'no ' : 'yes'}]`).should('be.checked');
  });
}

describe('Resubmit an Audit', () => {
  beforeEach(() => {
    cy.visit('/');
    testLoginGovLogin();
    cy.visit('/audit/resubmission-start');
  });

  afterEach(() => {
    testLogoutGov();
  });

  describe('Invalid report_ids', () => {
    it('Cancel', () => {
      cy.get('[id=cancel]').click();
      cy.url().should('include', '/audit');
    });

    it('Blank report ID', () => {
      cy.get('[id=continue]').click();
      cy.url().should('include', '/resubmission-start');
      cy.get('[id=error]').contains('This field is required.');
    });

    it('Short report ID', () => {
      cy.get('[id=report_id]').type('TOO-SHORT');
      cy.get('[id=continue]').click();
      cy.url().should('include', '/resubmission-start');
      cy.get('[id=error]').contains('The given report ID is too short!');
    });

    it('Long report ID', () => {
      cy.get('[id=report_id]').type('WAYYYYY-TOOOOOOO-LONGGGGGGGGGG');
      cy.get('[id=continue]').click();
      cy.url().should('include', '/resubmission-start');
      cy.get('[id=error]').contains('The given report ID is too long!');
    });

    it('Report ID not found', () => {
      cy.get('[id=report_id]').type('YYYY-MM-SOURCE-0123456789');
      cy.get('[id=continue]').click();
      cy.url().should('include', '/resubmission-start');
      cy.get('[id=error]').contains('Audit to resubmit not found.');
    });
  });

  describe('Valid report_ids', () => {
    it('Checklist banner', () => {
      // Replace with a report_id of a normal audit:
      // submission_status = 'disseminated'
      const previous_report_id = 'REPLACE-ME'
      cy.get('[id=report_id]').type(previous_report_id);
      cy.get('[id=continue]').click();
      cy.url().should('include', '/report_submission/eligibility/');
      testInitializeAudit(false, true);
      cy.url().should('include', '/audit/submission-progress/');
      cy.get('[id=resubmission-banner]').contains(`Resubmission of ${previous_report_id} in progress.`);
    });

    // Replace with a report_id of a public, tribal audit:
    // submission_status = 'disseminated'
    // and tribal_data_consent->is_tribal_information_authorized_to_be_public = true
    it('Previous was tribal public', () => {
      const previous_report_id = 'REPLACE-ME'
      testTribal(previous_report_id, false);
    });

    // Replace with a report_id of a non-public, tribal audit:
    // submission_status = 'disseminated'
    // and tribal_data_consent->is_tribal_information_authorized_to_be_public = false
    it.only('Previous was tribal non-public', () => {
      const previous_report_id = 'REPLACE-ME'
      testTribal(previous_report_id, true);
    });
  });
});
