export function testPdfAuditReport() {
  cy.get('[id_test="test-financial_statements"]').type(1);
  cy.get('[id_test="test-financial_statements_opinion"]').type(1);
  cy.get('[id_test="test-schedule_expenditures"]').type(1);
  cy.get('[id_test="test-schedule_expenditures_opinion"]').type(1);
  cy.get('[id_test="test-uniform_guidance_control"]').type(1);
  cy.get('[id_test="test-uniform_guidance_compliance"]').type(1);
  cy.get('[id_test="test-GAS_control"]').type(1);
  cy.get('[id_test="test-GAS_compliance"]').type(1);
  cy.get('[id_test="test-schedule_findings"]').type(1);
  cy.get('[id_test="test-schedule_prior_findings"]').type(1);
  cy.get('[id_test="test-CAP_page"]').type(1);

  cy.get('#upload_report').selectFile('cypress/fixtures/basic.pdf');
  cy.get('#continue').click(); // Performs upload and return to main page
}

