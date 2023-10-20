import 'cypress-file-upload';
import { testFederalAwards } from '../support/federal-awards.js';
import { testFileUploadMsg } from '../support/file-uploaded-msg.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import {
  testWorkbookAdditionalUEIs,
} from '../support/workbook-uploads.js';

describe('Additional UEIs page', () => {
  before(() => {
    cy.visit('/');
    cy.url().should('include', '/');
    testLoginGovLogin();
  });

  it('Additional UEIs uploads successfully', () => {
    testFederalAwards();

    cy.get(".usa-link").contains("Additional UEIs").click();
    testWorkbookAdditionalUEIs(false);
  });

  it('Displays message if file has already been uploaded', () => {
    testFileUploadMsg('Edit the Additional UEIs');
  });
});
