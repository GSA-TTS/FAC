import 'cypress-file-upload';

describe('Federal awards page', () => {
  before(() => {
    cy.visit('/report_submission/federal-awards/2022JUN0001000001');
  });
  it('Page loads successfully', () => {
    cy.url().should('include', '/report_submission/federal-awards/2022JUN0001000001');
  });

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
  });

  describe('File already uploaded', () => {
    it('Displays message if file has already been uploaded', () => {
      cy.visit('/report_submission/federal-awards/2022JUN0001000001');
      cy.get('#already-submitted')
        .invoke('text')
        .then((text) => {
          const expectedText = 'A file has already been uploaded for this section. A successful reupload will overwrite your previous submission.';
          expect(text.trim()).to.equal(expectedText);
        });
    });
  });

  describe('File upload failure', () => {
    it('unsuccessful upload Federal Award', () => {
      //cy.intercept('/audit/excel/federal-awards-expended/*', {
      // statusCode: 400,
      // fixture: 'fail-res.json',
      // }).as('uploadFail');
      cy.visit('report_submission/federal-awards/2022JUN0001000001');
      cy.get('#file-input-federal-awards-xlsx').attachFile('findings-text-test-valid.xlsx');
      // cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
    });
  });
});
