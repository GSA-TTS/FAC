import 'cypress-file-upload';

describe('Audit findings page', () => {
    before(() => {
      cy.visit('/report_submission/CAP/2022XB40001000002');
    });
    it('Page loads successfully', () => {
      cy.url().should('include','/report_submission/CAP/2022XB40001000002');
    });

  });

  describe('File upload successful', () => {
    it('Successfully uploads CAP', () => {
      cy.intercept('/audit/excel/CorrectiveActionPlan/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.visit('report_submission/CAP/2022XB40001000002');
      cy.get('#file-input-CAP-xlsx').attachFile('CorrectiveActionPlanTemplate2019-2022.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    })

    describe('File upload fail', () => {
      it('unsuccessful upload CAP', () => {
        cy.intercept('POST','/audit/excel/CorrectiveActionPlan/*', {
          statusCode: 400,
          fixture: 'fail-res.json', }).as('uploadFail')
        cy.visit('report_submission/CAP/2022XB40001000002');
        cy.get('#file-input-CAP-xlsx').attachFile('FederalAwardsExpendedTemplateUG2019.xlsx');
        cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
        cy.wait(2000).get('#info_box').should('have.text','Error on validation. See console for more information.');
      })
    })
  });