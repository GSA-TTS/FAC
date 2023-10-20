import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testPdfAuditReport } from '../support/report-pdf.js';
import { testLoginGovLogin } from '../support/login-gov.js';

describe('Audit report PDF page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Audit report PDF uploads successfully', () => {
    testFederalAwards();

    cy.get(".usa-link").contains("Audit report PDF").click();
    testPdfAuditReport(false);
  });

  it('Displays message if file has already been uploaded', () => {
    cy.visit(`/audit/`);
    cy.url().should('match', /\/audit\//);
    cy.get(':nth-child(4) > .usa-table > tbody > tr').last().find('td:nth-child(1)>.usa-link').click();
    cy.get('.usa-link').contains('Edit the Audit report PDF').click();
    cy.get('#already-submitted')
      .invoke('text')
      .then((text) => {
        const expectedText = 'A file has already been uploaded for this section. A successful reupload will overwrite your previous submission.';
        expect(text.trim()).to.equal(expectedText);
      });
  });
});
