export function testPdfAuditReport() {
  cy.get('#financial_statements').type(1);
  cy.get('#financial_statements_opinion').type(1);
  cy.get('#schedule_expenditures').type(1);
  cy.get('#schedule_expenditures_opinion').type(1);
  cy.get('#uniform_guidance_control').type(1);
  cy.get('#uniform_guidance_compliance').type(1);
  cy.get('#GAS_control').type(1);
  cy.get('#GAS_compliance').type(1);
  cy.get('#schedule_findings').type(1);
  cy.get('#schedule_prior_findings').type(1);
  cy.get('#CAP_page').type(1);

  cy.get('#upload_report').selectFile('cypress/fixtures/basic.pdf');
  cy.get('#continue').click();
}
