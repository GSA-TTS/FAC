import { login_gov_login } from '../support/login_gov.js';

describe('Full audit submission', () => {
  before(() => {
    cy.visit('/');
  });

  it('Loads the home page', () => {
    cy.url().should('include', '/');
  });

  it('Logs in with Login.gov', () => {
    login_gov_login();
  });
});
