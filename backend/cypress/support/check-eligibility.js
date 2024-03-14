// Resusable components for the "Check Eligibility" pre-screener

export function selectValidEntries(isTribal) {
  cy.get(`label[for=entity-${isTribal ? 'tribe' : 'state'}]`).click();
  cy.get('label[for=spend-yes]').click();
  cy.get('label[for=us-yes]').click();
}

export function testValidEligibility(isTribal) {
  selectValidEntries(isTribal);

  cy.get('.usa-button').contains('Continue').click();
  cy.url().should('match', /\/report_submission\/auditeeinfo\/$/);
}
