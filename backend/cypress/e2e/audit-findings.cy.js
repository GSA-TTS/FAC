import 'cypress-file-upload';

describe('Audit findings page', () => {
  const reportTestId = '2023MAY0001000001'

  before(() => {
    cy.visit(`/report_submission/audit-findings/${reportTestId}`);
  });
  it('Page loads successfully', () => {
    cy.url().should('include', `/report_submission/audit-findings/${reportTestId}`);
  });

  describe('File upload successful', () => {
    it('Successfully uploads audit findings', () => {
      cy.intercept('/audit/excel/findings-uniform-guidance/*', {
        fixture: 'success-res.json',
      }).as('uploadSuccess')
      cy.visit(`/report_submission/audit-findings/${reportTestId}`);
      cy.get('#file-input-audit-findings-xlsx').attachFile('findings-Test.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
      cy.get('#continue').click();
    })
  });

  describe('File upload fail', () => {
    it('unsuccessful upload audit findings', () => {
      cy.intercept('POST', '/audit/excel/findings-uniform-guidance/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail')
      cy.visit(`/report_submission/audit-findings/${reportTestId}`);
      cy.get('#file-input-audit-findings-xlsx').attachFile('federal-awards-Test.xlsx');
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
    })
  })

});