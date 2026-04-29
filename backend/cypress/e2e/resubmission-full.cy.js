import { testFullSubmission } from '../support/full-submission.js';
import { testLoginGovLogin } from '../support/login-gov.js';

describe('Full audit resubmission', () => {
  it('Non-tribal, public', () => {
    testFullSubmission(false, true).then((previous_report_id_1) => {
      testLoginGovLogin();

      cy.visit('/audit/resubmission-start');
      cy.get('#id_material_change_reasons_0').check({ force: true });
      cy.get('#report_id').type(previous_report_id_1);
      cy.get('#continue').click();
      cy.url().should('include', '/report_submission/eligibility/');

      testFullSubmission(false, true, true).then((previous_report_id_2) => {
        testLoginGovLogin();

        cy.visit('/audit/resubmission-start');
        cy.get('#id_material_change_reasons_0').check({ force: true });
        cy.get('#report_id').type(previous_report_id_2);
        cy.get('#continue').click();
        cy.url().should('include', '/report_submission/eligibility/');

        testFullSubmission(false, true, true)
      });
    });
  });
});
