import 'cypress-file-upload';

describe('Audit findings page', () => {
  const reportTestId = '2023MAY0001000001'

  before(() => {
    cy.visit(`/report_submission/CAP/${reportTestId}`);
  });
  it('Page loads successfully', () => {
    cy.url().should('include', `/report_submission/CAP/${reportTestId}`);
  });

  describe('File upload successful', () => {
    it('Successfully uploads CAP', () => {
      cy.intercept('/audit/excel/corrective-action-plan/*', {
        fixture: 'success-res.json',
      }).as('uploadSuccess')
      cy.visit(`/report_submission/CAP/${reportTestId}`);
      cy.get('#file-input-CAP-xlsx').attachFile('corrective-action-plan-Test.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
      cy.get('#continue').click();
      cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    })

    describe('File upload fail', () => {
      it('unsuccessful upload CAP', () => {
        cy.intercept('POST', '/audit/excel/corrective-action-plan/*', {
          statusCode: 400,
          fixture: 'fail-res.json',
        }).as('uploadFail')
        cy.visit(`/report_submission/CAP/${reportTestId}`);
        cy.get('#file-input-CAP-xlsx').attachFile('cap-invalid.xlsx');
        cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
        cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
      })
    })
  });
});