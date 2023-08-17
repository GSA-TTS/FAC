export function testCrossValidation() {
  cy.url().should('match', /\/audit\/cross-validation\/[0-9A-Z]{17}/);

  // Cross val runs and passes
  cy.get(".usa-button").contains("Begin Validation").click();
  cy.get('.usa-fieldset').contains('No errors were found.');

  // Continue to the lock screen
  cy.get('.usa-button').contains('Proceed to certification').click();
  cy.url().should('match', /\/audit\/ready-for-certification\/[0-9A-Z]{17}/);

  // Lock the submission for the certification steps
  cy.get('.usa-button').contains('Lock for certification').click();
  cy.url().should('match', /\/audit\/submission-progress\/[0-9A-Z]{17}/);
}
