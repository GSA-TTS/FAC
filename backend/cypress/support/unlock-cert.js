
// test unlock certification
export function testUnlock(){
  cy.get(".usa-button").contains("Unlock").click();
  cy.get('img[alt="FAC.gov"]').should('exist').click();
  cy.url().should('match', /\/audit\//);
  cy.get('table.usa-table.margin-top-0.pa11y-ignore tbody > tr:last-child').should('contain', 'Unlock')
  cy.contains('Ready for Certification').click();
  cy.url().should('match', /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
}