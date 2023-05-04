import 'cypress-file-upload';
require("@4tw/cypress-drag-drop");


describe('File upload successful', () => {
    it('Successfully uploads Federal Awards', () => {
      cy.visit('report_submission/federal-awards/2022XB40001000002');
      cy.get('#file-input-federal-awards-xlsx').attachFile('FederalAwardsExpendedTemplateUG2019.xlsx');
      cy.intercept('/audit/excel/FederalAwardsExpended/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    });
    
    it('Successfully uploads audit findings', () => {
      cy.visit('report_submission/audit-findings/2022XB40001000002');
      cy.get('#file-input-audit-findings-xlsx').attachFile('FindingsUniformGuidanceTemplate2019-2022.xlsx');
      cy.intercept('/audit/excel/FindingsUniformGuidance/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    })

    it('Successfully uploads audit findings text', () => {
      cy.visit('report_submission/audit-findings-text/2022XB40001000002');
      cy.get('#file-input-audit-findings-text-xlsx').attachFile('FindingsText2019-2022.xlsx');
      cy.intercept('/audit/excel/FindingsText/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    })
    
    it('Successfully uploads CAP', () => {
      cy.visit('report_submission/CAP/2022XB40001000002');
      cy.get('#file-input-CAP-xlsx').attachFile('CorrectiveActionPlanTemplate2019-2022.xlsx');
      cy.intercept('/audit/excel/CorrectiveActionPlan/*', {
        fixture: 'success-res.json', }).as('uploadSuccess')
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
      cy.get('#continue').click();
    })


    // it('Federal Awards drag and drop upload', () => {
    //   cy.visit('report_submission/federal-awards/20225DZ0001000001');
    //   const source = cy.get('#file-input-federal-awards-xlsx');
    //   const target = cy.get('#drop-target');
    //   // trigger the drag-and-drop event sequence
    //   source.trigger('dragstart');
    //   target.trigger('dragenter');
    //   target.trigger('dragover');
    //   target.trigger('drop');
    //   source.trigger('dragend');
    //   // wait for the file to be processed
    //   cy.wait(10000);
    //   // assert that the file was uploaded successfully
    //   cy.get('#file-input-federal-awards-xlsx').contains('FederalAwardsExpendedTemplateUG2019.xlsx');
    //   cy.get('#continue').click();
    //   cy.wait(10000);
    //   cy.get('#info_box').should('have.text','File successfully validated!');
    // });
  })
