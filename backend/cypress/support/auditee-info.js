// re-usable code for testing the Auditee Info form

export function testValidAuditeeInfo() {
  cy.intercept('POST', '/api/sac/ueivalidation', {
    fixture: 'sam-gov-api-mock.json',
  }).as('uei_check_success');

  cy.visit('/report_submission/auditeeinfo/');

  // Hard-coding some UEI which may eventually become unregistered 
  // // This UEI needs to match up with the UEI in the workbooks.
  cy.get('#auditee_uei').clear();
  cy.get('#auditee_uei').type('D7A4J33FUMJ1');

  // Now fill in the audit dates
  cy.get('#auditee_fiscal_period_start').clear();
  cy.get('#auditee_fiscal_period_start').type('01/01/2023');

  cy.get('#auditee_fiscal_period_end').clear();
  cy.get('#auditee_fiscal_period_end').type('12/31/2023');

  cy.get('#continue').should('not.be.disabled');
  cy.get('#continue').click();

  // Wait for API + for modal to finish loading (this is why the button was display:none)
  cy.wait('@uei_check_success');
  cy.get('.uei-search-result').should('be.visible');
  cy.get('.uei-search-result').should('not.have.class', 'loading');

  // Success modal primary is "Continue" (duplicates modal primary is "Yes, continue")
  cy.get('#uei-search-result .usa-modal__footer button.primary')
    .should('be.visible')
    .contains('Continue')
    .click();
    
  // and assert on the URL we end up at
  cy.url().should('match', /\/report_submission\/eligibility\/$/);
}
