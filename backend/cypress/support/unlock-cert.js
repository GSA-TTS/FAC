import { testCrossValidation } from "./cross-validation";

// test unlock certification
export function testUnlock(){
  cy.get('.usa-button').contains('Unlock').click();
  cy.get('#continue').contains('Unlock submission').click();
  cy.get('img[alt="FAC.gov"]').should('exist').click();
  cy.url().should('match', /\/audit\//);
  cy.get('table.usa-table.margin-top-0.pa11y-ignore tbody > tr:last-child .usa-link').contains('In Progress').click();
  cy.url().should('match', /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
  cy.then(() => {
    cy.get(".usa-link").contains("Pre-submission validation").click();
    testCrossValidation();
  });
}