import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import {
  testWorkbookNotesToSEFA
} from '../support/workbook-uploads.js';

describe('Notes to SEFA page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Notes to SEFA uploads successfully', () => {
    testFederalAwards();

    cy.get(".usa-link").contains("Notes to SEFA").click();
    testWorkbookNotesToSEFA(false);
  });

  it('Displays message if file has already been uploaded', () => {
    testFileUploadMsg('Edit the Notes to SEFA');
  });
});
