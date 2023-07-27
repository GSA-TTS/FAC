import { testLoginGovLogin } from '../support/login_gov.js';

describe('Full audit submission', () => {
  before(() => {
    cy.visit('/');
  });

  it('Loads the home page', () => {
    cy.url().should('include', '/');
  });

  it('Logs in with Login.gov', () => {
    testLoginGovLogin();
  });

  // finishes on `/audit/`
  // check the terms and conditions box and click "Start a new submission"
  cy.get('label[for=check-start-new-submission]').click();
  cy.get('.usa-button').contains('Start a new submission').click();
  cy.url().should('match', /\/report_submission\/eligibility\/$/);

});
