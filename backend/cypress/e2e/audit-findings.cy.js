import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import {
  testWorkbookFindingsUniformGuidance,
} from '../support/workbook-uploads.js';

describe('Audit Findings page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Audit Findings uploads successfully', () => {
    testFederalAwards();
    cy.get(".usa-link").contains("Federal Awards Audit Findings").click();
    testWorkbookFindingsUniformGuidance(false);
    testFileUploadMsg('Edit the Federal Awards Audit Findings');
  });
});
