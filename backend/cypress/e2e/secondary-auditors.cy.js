import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import {
    testWorkbookSecondaryAuditors,
} from '../support/workbook-uploads.js';

describe('Secondary Auditors page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Secondary auditors uploads successfully', () => {
    testFederalAwards();
    cy.get(".usa-link").contains("Secondary Auditors").click();
    testWorkbookSecondaryAuditors(false);
    testFileUploadMsg('Edit the Secondary Auditors');
  });
});
