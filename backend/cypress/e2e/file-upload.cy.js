import 'cypress-file-upload';
require("@4tw/cypress-drag-drop");


describe('File upload successful', () => {
    it('Successfully uploads Federal Awards', () => {
      cy.intercept('/audit/excel/FederalAwardsExpended/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.visit('report_submission/federal-awards/2022XB40001000002');
      cy.get('#file-input-federal-awards-xlsx').attachFile('FederalAwardsExpendedTemplateUG2019.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    });
    
    it('Successfully uploads audit findings', () => {
      cy.intercept('/audit/excel/FindingsUniformGuidance/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.visit('report_submission/audit-findings/2022XB40001000002');
      cy.get('#file-input-audit-findings-xlsx').attachFile('FindingsUniformGuidanceTemplate2019-2022.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    });

    it('Successfully uploads audit findings text', () => {
      cy.intercept('/audit/excel/FindingsText/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.visit('report_submission/audit-findings-text/2022XB40001000002');
      cy.get('#file-input-audit-findings-text-xlsx').attachFile('FindingsText2019-2022.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    });
    
    it('Successfully uploads CAP', () => {
      cy.intercept('/audit/excel/CorrectiveActionPlan/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.visit('report_submission/CAP/2022XB40001000002');
      cy.get('#file-input-CAP-xlsx').attachFile('CorrectiveActionPlanTemplate2019-2022.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    });


    describe('File upload fail', () => {
      it('unsuccessful upload Federal Award', () => {
        cy.intercept('POST','/audit/excel/FederalAwardsExpended/*', {
          statusCode: 400,
          fixture: 'fail-res.json', }).as('uploadFail')
        cy.visit('report_submission/federal-awards/2022XB40001000002');
        cy.get('#file-input-federal-awards-xlsx').attachFile('FindingsUniformGuidanceTemplate2019-2022.xlsx');
        cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
        cy.wait(2000).get('#info_box').should('have.text','Error on validation. See console for more information.');
      })

      it('unsuccessful upload audit findings', () => {
        cy.intercept('POST','/audit/excel/FindingsUniformGuidance/*', {
          statusCode: 400,
          fixture: 'fail-res.json', }).as('uploadFail')
        cy.visit('report_submission/audit-findings/2022XB40001000002');
        cy.get('#file-input-audit-findings-xlsx').attachFile('FederalAwardsExpendedTemplateUG2019.xlsx');
        cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
        cy.wait(2000).get('#info_box').should('have.text','Error on validation. See console for more information.');
      })

      it('unsuccessful upload audit findings text', () => {
        cy.intercept('POST','/audit/excel/FindingsText/*', {
          statusCode: 400,
          fixture: 'fail-res.json', }).as('uploadFail')
        cy.visit('report_submission/audit-findings-text/2022XB40001000002');
        cy.get('#file-input-audit-findings-text-xlsx').attachFile('FederalAwardsExpendedTemplateUG2019.xlsx');
        cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
        cy.wait(2000).get('#info_box').should('have.text','Error on validation. See console for more information.');
      })

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
    
  })
