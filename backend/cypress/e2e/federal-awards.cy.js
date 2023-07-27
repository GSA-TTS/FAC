import 'cypress-file-upload';

describe('Federal awards page', () => {
  const reportTestId = '2023MAY0001000001'

  before(() => {
    cy.visit(`/report_submission/federal-awards/${reportTestId}`);
  });
  it('Page loads successfully', () => {
    cy.url().should('include', `/report_submission/federal-awards/${reportTestId}`);
  });

  describe('File upload successful', () => {
    it('Successfully uploads Federal Awards', () => {
      cy.intercept('/audit/excel/federal-awards-expended/*', {
        fixture: 'success-res.json',
      }).as('uploadSuccess')
      cy.visit(`report_submission/federal-awards/${reportTestId}`);
      cy.get('#file-input-federal-awards-xlsx').attachFile('federal-awards-expended-UPDATE.xlsx');
      cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
      cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
      cy.get('#continue').click();
      cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    });
  });

  describe('File already uploaded', () => {
    it('Displays message if file has already been uploaded', () => {
      cy.visit(`/report_submission/federal-awards/${reportTestId}`);
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
      cy.intercept('/audit/excel/federal-awards-expended/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail');
      cy.visit(`/report_submission/federal-awards/${reportTestId}`);
      cy.get('#file-input-federal-awards-xlsx').attachFile('fed-awards-invalid.xlsx');
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
      cy.wait(2000).get('#info_box').should('contain', 'A field is missing');
    });
  });
});
