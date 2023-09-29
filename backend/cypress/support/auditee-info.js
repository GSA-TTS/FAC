// re-usable code for testing the Auditee Info form

export function testValidAuditeeInfo() {
  cy.intercept('api/sac/ueivalidation', {
    fixture: 'sam-gov-api-mock.json',
  }).as('uei_check_success')

  // Hard-coding some UEI which may eventually become unregistered
  // This UEI needs to match up with the UEI in the workbooks.
  cy.get('#auditee_uei').type('D7A4J33FUMJ1');
  cy.get('#auditee_uei-btn').click().wait('@uei_check_success');
  // modal search result box needs "Continue" to be clicked
  cy.get('button[data-close-modal]').contains('Continue').click();

  // Now fill in the audit dates
  cy.get('#auditee_fiscal_period_start').type("01/01/2022");
  cy.get('#auditee_fiscal_period_end').type("12/31/2022");

  // and click continue
  cy.get('.usa-button').contains('Continue').click();

  // and assert on the URL we end up at
  cy.url().should('match', /\/report_submission\/accessandsubmission\/$/);
}
