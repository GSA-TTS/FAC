// re-usable code for testing the Auditee Info form

export function testValidAuditeeInfo() {
  // hard-coding some UEI which may eventually become unregistered
  cy.get('#auditee_uei').type('LZGKJ22EF7B5');
  cy.get('#auditee_uei-btn').click();
  // modal search result box needs "Continue" to be clicked
  cy.get('button[data-close-modal]').contains('Continue').click();

  // Now fill in the audit dates
  let today = new Date().toLocaleDateString();
  cy.get('#auditee_fiscal_period_start').type(today);
  cy.get('#auditee_fiscal_period_end').type(today);

  // and click continue
  cy.get('.usa-button').contains('Continue').click();

  // and assert on the URL we end up at
  cy.url().should('match', /\/report_submission\/accessandsubmission\/$/);
}
