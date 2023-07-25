import 'cypress-file-upload';

describe('Audit findings text page', () => {
  const reportTestId = '2023MAY0001000001'

  before(() => {
    cy.visit(`/report_submission/audit-findings-text/${reportTestId}`);
  });
  it('Page loads successfully', () => {
    cy.url().should('include', `/report_submission/audit-findings-text/${reportTestId}`);
  });

  describe('findings text workbook upload successful', () => {
    it('Successfully uploads audit findings text', () => {
      cy.intercept('/audit/excel/findings-text/*', {
        fixture: 'success-res.json',
      }).as('uploadSuccess')
      cy.visit(`/report_submission/audit-findings-text/${reportTestId}`);
      cy.get('#file-input-audit-findings-text-xlsx').attachFile('findings-text-UPDATE.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
      cy.get('#continue').click();
      cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    })
  });

  describe('File upload fail', () => {
    it('unsuccessful upload audit findings text', () => {
      cy.intercept('POST', '/audit/excel/findings-text/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail')
      cy.visit(`/report_submission/audit-findings-text/${reportTestId}`);
      cy.get('#file-input-audit-findings-text-xlsx').attachFile('federal-awards-Test.xlsx');
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
    })
  })

});