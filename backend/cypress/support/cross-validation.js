export function testCrossValidation() {
  cy.url().should('match', /\/audit\/cross-validation\/[0-9A-Z]{17}/);
  cy.get(".usa-button").contains("Begin Validation").click();
  cy.get('.usa-fieldset').contains('No errors were found.');
}
