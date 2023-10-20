import 'cypress-file-upload';
import { testValidAccess } from '../support/check-access.js';
import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';
import { testValidGeneralInfo } from '../support/general-info.js';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import {
  testWorkbookFindingsText,
} from '../support/workbook-uploads.js';

describe('Audit Findings Text page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Audit Findings Text uploads successfully', () => {
    testFederalAwards();
    cy.get(".usa-link").contains("Federal Awards Audit Findings Text").click();
    testWorkbookFindingsText(false);
    testFileUploadMsg('Edit the Federal Awards Audit Findings Text');
  });
});
