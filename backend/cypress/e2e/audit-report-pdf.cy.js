import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import { testPdfAuditReport } from '../support/report-pdf.js';

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
    testFileUploadMsg('Edit the Audit report PDF');
  });
});
