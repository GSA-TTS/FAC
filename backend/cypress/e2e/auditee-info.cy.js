import { testValidAuditeeInfo } from '../support/auditee-info.js';

describe('Auditee info form', () => {
  it('Can fill out a valid form', () => {
    cy.visit('/');
    cy.login();
    cy.visit('report_submission/auditeeinfo');
    testValidAuditeeInfo();
  });
});
