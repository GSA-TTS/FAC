import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import {
  testWorkbookAdditionalEINs,
} from '../support/workbook-uploads.js';

describe('Additional EINs page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Additional EINs uploads successfully', () => {
    testFederalAwards();
    cy.get(".usa-link").contains("Additional EINs").click();
    testWorkbookAdditionalEINs(false);
    testFileUploadMsg('Edit the Additional EINs');
  });
});
