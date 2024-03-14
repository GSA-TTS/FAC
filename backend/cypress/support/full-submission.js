import { testCrossValidation } from './cross-validation.js';
import { testLoginGovLogin } from './login-gov.js';
import { testLogoutGov } from './logout-gov.js';
import { testAuditInformationForm } from './audit-info-form.js';
import { testPdfAuditReport } from './report-pdf.js';
import { testAuditorCertification } from './auditor-certification.js';
import { testAuditeeCertification } from './auditee-certification.js';
import { testReportIdFoundWithTribalAccess, testReportIdFoundWithoutTribalAccess, testReportIdNotFoundWithoutTribalAccess } from './dissemination-table.js';
import { testTribalAuditPublic, testTribalAuditPrivate } from './tribal-audit-form.js';
import { testInitializeAudit } from './initialize-audit.js';
import { testUnlock } from './unlock-cert.js';
import {
  testWorkbookFederalAwards,
  testWorkbookNotesToSEFA,
  testWorkbookFindingsUniformGuidance,
  testWorkbookFindingsText,
  testWorkbookCorrectiveActionPlan,
  testWorkbookAdditionalUEIs,
  testWorkbookSecondaryAuditors,
  testWorkbookAdditionalEINs
} from './workbook-uploads.js';

const LOGIN_TEST_EMAIL_AUDITEE = Cypress.env('LOGIN_TEST_EMAIL_AUDITEE');
const LOGIN_TEST_PASSWORD_AUDITEE = Cypress.env('LOGIN_TEST_PASSWORD_AUDITEE');
const LOGIN_TEST_OTP_SECRET_AUDITEE = Cypress.env('LOGIN_TEST_OTP_SECRET_AUDITEE');

export function testFullSubmission(isTribal, isPublic) {
  cy.visit('/');
  cy.url().should('include', '/');

  // Logs in with Login.gov'
  testLoginGovLogin();

  testInitializeAudit(isTribal);

  // Upload all the workbooks. Don't intercept the uploads, which means a file will make it into the DB.
  cy.get(".usa-link").contains("Federal Awards").click();
  testWorkbookFederalAwards(false);

  cy.get(".usa-link").contains("Notes to SEFA").click();
  testWorkbookNotesToSEFA(false);

  cy.get(".usa-link").contains("Audit report PDF").click();
  testPdfAuditReport(false);

  cy.get(".usa-link").contains("Federal Awards Audit Findings").click();
  testWorkbookFindingsUniformGuidance(false);

  cy.get(".usa-link").contains("Federal Awards Audit Findings Text").click();
  testWorkbookFindingsText(false);

  cy.get(".usa-link").contains("Corrective Action Plan").click();
  testWorkbookCorrectiveActionPlan(false);

  cy.get(".usa-link").contains("Additional UEIs").click();
  testWorkbookAdditionalUEIs(false);

  cy.get(".usa-link").contains("Secondary Auditors").click();
  testWorkbookSecondaryAuditors(false);

  cy.get(".usa-link").contains("Additional EINs").click();
  testWorkbookAdditionalEINs(false);

  if (isTribal) {
    cy.url().then(url => {
      const reportId = url.split('/').pop();

      // Complete the tribal audit form as auditee - opt private
      testLogoutGov();
      testLoginGovLogin(
        LOGIN_TEST_EMAIL_AUDITEE,
        LOGIN_TEST_PASSWORD_AUDITEE,
        LOGIN_TEST_OTP_SECRET_AUDITEE
      );
      cy.visit(`/audit/submission-progress/${reportId}`);
      cy.get(".usa-link").contains("Tribal data release").click();

      if (isPublic) {
        testTribalAuditPublic();
      } else {
        testTribalAuditPrivate();
      }

      // Login as Auditor
      testLogoutGov();
      testLoginGovLogin();
      cy.visit(`/audit/submission-progress/${reportId}`);
    })
  }

  // Complete the audit information form
  cy.get(".usa-link").contains("Audit Information form").click();
  testAuditInformationForm();

  cy.get(".usa-link").contains("Pre-submission validation").click();
  testCrossValidation();

  // test unlock certification
  testUnlock();

  // Auditor certification
  cy.get(".usa-link").contains("Auditor Certification").click();
  testAuditorCertification();

  // Grab the report ID from the URL
  cy.url().then(url => {
    const reportId = url.split('/').pop();

    testLogoutGov();

    // Login as Auditee
    testLoginGovLogin(
      LOGIN_TEST_EMAIL_AUDITEE,
      LOGIN_TEST_PASSWORD_AUDITEE,
      LOGIN_TEST_OTP_SECRET_AUDITEE
    );

    cy.visit(`/audit/submission-progress/${reportId}`);

    // Auditee certification
    cy.get(".usa-link").contains("Auditee Certification").click();
    testAuditeeCertification();

    // Submit
    cy.get(".usa-link").contains("Submit to the FAC for processing").click();
    cy.url().should('match', /\/audit\/submission\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
    cy.get('#continue').click();
    cy.url().should('match', /\/audit\//);

    // The report ID should be found in the Completed Audits table
    cy.get('.usa-table').contains(
      'caption',
      /audits are complete/
    ).siblings().contains('td', reportId);

    // The Report should not be in the dissemination table
    if (isPublic) {
      testReportIdFoundWithoutTribalAccess(reportId);
      testReportIdFoundWithTribalAccess(reportId);
    } else {
      testReportIdNotFoundWithoutTribalAccess(reportId);
      testReportIdFoundWithTribalAccess(reportId);
    }
  });

  testLogoutGov();
}
