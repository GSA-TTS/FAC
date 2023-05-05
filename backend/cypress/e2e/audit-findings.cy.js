import 'cypress-file-upload';

describe('Audit findings page', () => {
    before(() => {
      cy.visit('/report_submission/audit-findings/2022XB40001000002');
    });
    it('Page loads successfully', () => {
      cy.url().should('include','/report_submission/audit-findings/2022XB40001000002');
    });

    // it('Page fails to loads unsuccessfully', () => {
    //     cy.request({
    //         url:'/report_submission/audit-findings/',
    //     }).then((reponse) => {
    //         expect(response.status).to.eq(404);
    //     });
    // });


    describe('File upload successful', () => {
      it('Successfully uploads audit findings', () => {
        cy.intercept('/audit/excel/FindingsUniformGuidance/*', {
          fixture: 'success-res.json', }).as('uploadSuccess')
        cy.visit('report_submission/audit-findings/2022XB40001000002');
        cy.get('#file-input-audit-findings-xlsx').attachFile('FindingsUniformGuidanceTemplate2019-2022.xlsx');
        cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
        cy.wait(2000).get('#info_box').should('have.text','File successfully validated!');
        cy.get('#continue').click();
      })
   });

   describe('File upload fail', () => {
    it('unsuccessful upload audit findings', () => {
      cy.intercept('POST','/audit/excel/FindingsUniformGuidance/*', {
        statusCode: 400,
        fixture: 'fail-res.json', }).as('uploadFail')
      cy.visit('report_submission/audit-findings/2022XB40001000002');
      cy.get('#file-input-audit-findings-xlsx').attachFile('FederalAwardsExpendedTemplateUG2019.xlsx');
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text','Error on validation. See console for more information.');
    })
  })
  
  });