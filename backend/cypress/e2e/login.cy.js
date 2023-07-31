import { testLoginGovLogin } from '../support/login-gov.js';

describe('login', () => {
  // To set DISABLE_AUTH in Cypress, set the environment variable
  // CYPRESS_DISABLE_AUTH in the OS. If it's not set, default to false
  const disableAuth = Cypress.env('DISABLE_AUTH') || false;

  beforeEach(() => {
    cy.visit('/');
  });

  it('Page loads successfully', () => {
    cy.url().should('include', '/');
  });

  //This uses a IF/ Else statement whether authentication is required based if DISABLE_AUTH is True/False
  describe('authenticating', () => {
    if (!disableAuth) {
      it('should use Login.gov', () => {
        testLoginGovLogin();
      });
    } else {
      it('should not require authentication', () => {
        cy.url().should('match', /\/audit\/$/);
      });
    }
  });
});
