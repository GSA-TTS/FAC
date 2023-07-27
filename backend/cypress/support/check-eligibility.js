// Resusable components for the "Check Eligibility" pre-screener

export function selectValidEntries() {
  cy.get('label[for=entity-state]').click();
  cy.get('label[for=spend-yes]').click();
  cy.get('label[for=us-yes]').click();
}

export function testValidEligibility() {
  selectValidEntries();

  cy.get('.usa-button').contains('Continue').click();
  cy.url().should('include', '/report_submission/auditeeinfo/');
}
