import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import {
  testWorkbookCorrectiveActionPlan,
} from '../support/workbook-uploads.js';

describe('Corrective Action Plan page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Corrective Action Plan uploads successfully', () => {
    testFederalAwards();

    cy.get(".usa-link").contains("Corrective Action Plan").click();
    testWorkbookCorrectiveActionPlan(false);
  });

  it('Displays message if file has already been uploaded', () => {
    testFileUploadMsg('Edit the Corrective Action Plan');
  });
});
