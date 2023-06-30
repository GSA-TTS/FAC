import 'cypress-file-upload';
//require("@4tw/cypress-drag-drop");


describe('File upload successful', () => {
  it('Successfully uploads Federal Awards', () => {
    cy.intercept('/audit/excel/federal-awards-expended/*', {
      fixture: 'success-res.json',
    }).as('uploadSuccess')
    cy.visit('report_submission/federal-awards/2022JUN0001000001');
    cy.get('#file-input-federal-awards-xlsx').attachFile('federal-awards-expended-test-valid.xlsx');
    cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
    cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
    cy.get('#continue').click();
    cy.url().should('contain', '/audit/submission-progress/2022JUN0001000001');
  });

  it('Successfully uploads audit findings', () => {
    cy.intercept('/audit/excel/findings-uniform-guidance/*', {
      fixture: 'success-res.json',
    }).as('uploadSuccess')
    cy.visit('report_submission/audit-findings/2022JUN0001000001');
    cy.get('#file-input-audit-findings-xlsx').attachFile('findings-uniform-guidance-test-valid.xlsx');
    cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
    cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
    cy.get('#continue').click();
    cy.url().should('contain', '/audit/submission-progress/2022JUN0001000001');
  });

  it('Successfully uploads audit findings text', () => {
    cy.intercept('/audit/excel/findings-text/*', {
      fixture: 'success-res.json',
    }).as('uploadSuccess')
    cy.visit('report_submission/audit-findings-text/2022JUN0001000001');
    cy.get('#file-input-audit-findings-text-xlsx').attachFile('findings-text-test-valid.xlsx');
    cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
    cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
    cy.get('#continue').click();
  });

  it('Successfully uploads CAP', () => {
    cy.intercept('/audit/excel/corrective-action-plan/*', {
      fixture: 'success-res.json',
    }).as('uploadSuccess')
    cy.visit('report_submission/CAP/2022JUN0001000001');
    cy.get('#file-input-CAP-xlsx').attachFile('corrective-action-plan-test-valid.xlsx');
    cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
    cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
    cy.get('#continue').click();
  });


  describe('File upload fail', () => {
    it('unsuccessful upload Federal Awards', () => {
      // cy.intercept('POST', '/audit/excel/federal-awards-expended/*', {
      // statusCode: 400,
      // fixture: 'fail-res.json',
      // }).as('uploadFail')
      cy.visit('report_submission/federal-awards/2022JUN0001000001');
      cy.get('#file-input-federal-awards-xlsx').attachFile('fed-awards-invalid.xlsx');
      // cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
    })

    it('unsuccessful upload audit findings', () => {
      // cy.intercept('POST', '/audit/excel/findings-uniform-guidance/*', {
      // statusCode: 400,
      // fixture: 'fail-res.json',
      //  }).as('uploadFail')
      cy.visit('report_submission/audit-findings/2022JUN0001000001');
      cy.get('#file-input-audit-findings-xlsx').attachFile('find-uni-invalid.xlsx');
      //cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
    })

    it('unsuccessful upload audit findings text', () => {
      // cy.intercept('POST', '/audit/excel/FindingsText/*', {
      //  statusCode: 400,
      // fixture: 'fail-res.json',
      // }).as('uploadFail')
      cy.visit('report_submission/audit-findings-text/2022JUN0001000001');
      cy.get('#file-input-audit-findings-text-xlsx').attachFile('find-text-invalid.xlsx');
      //cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
    })

    it('unsuccessful upload CAP', () => {
      // cy.intercept('POST', '/audit/excel/CorrectiveActionPlan/*', {
      //  statusCode: 400,
      //  fixture: 'fail-res.json',
      // }).as('uploadFail')
      cy.visit('report_submission/CAP/2022JUN0001000001');
      cy.get('#file-input-CAP-xlsx').attachFile('cap-invalid.xlsx');
      //  cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
    })
  })

})
