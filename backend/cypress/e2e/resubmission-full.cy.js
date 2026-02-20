import { testFullSubmission } from '../support/full-submission.js';
import { testLoginGovLogin } from '../support/login-gov.js';

describe('Full audit resubmission', () => {
  it('Non-tribal, public', () => {
    testFullSubmission(false, true).then((previous_report_id) => {
      testLoginGovLogin();

      cy.visit('/audit/resubmission-start');
      cy.get('[id=report_id]').type(previous_report_id);
      cy.get('[id=continue]').click();
      cy.url().should('include', '/report_submission/eligibility/');

      testFullSubmission(false, true, true);
    });
  });
});
