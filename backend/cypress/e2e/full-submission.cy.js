import { testCrossValidation } from '../support/cross-validation.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import { testLogoutGov } from '../support/logout-gov.js';
import { testValidAccess } from '../support/check-access.js';
import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';
import { testValidGeneralInfo } from '../support/general-info.js';
import { testAuditInformationForm } from '../support/audit-info-form.js';
import { testPdfAuditReport } from '../support/report-pdf.js';
import { testAuditorCertification } from '../support/auditor-certification.js';
import { testAuditeeCertification } from '../support/auditee-certification.js';
import {
  testWorkbookFederalAwards,
  testWorkbookNotesToSEFA,
  testWorkbookFindingsUniformGuidance,
  testWorkbookFindingsText,
  testWorkbookCorrectiveActionPlan,
  testWorkbookAdditionalUEIs,
  testWorkbookSecondaryAuditors,
  testWorkbookAdditionalEINs
} from '../support/workbook-uploads.js';

const LOGIN_TEST_EMAIL_AUDITEE = Cypress.env('LOGIN_TEST_EMAIL_AUDITEE');
const LOGIN_TEST_PASSWORD_AUDITEE = Cypress.env('LOGIN_TEST_PASSWORD_AUDITEE');
const LOGIN_TEST_OTP_SECRET_AUDITEE = Cypress.env('LOGIN_TEST_OTP_SECRET_AUDITEE');

describe('Full audit submission', () => {
  before(() => {
    cy.visit('/');
  });

  it('Completes a full submission', () => {
    cy.url().should('include', '/');

    // Logs in with Login.gov'
    testLoginGovLogin();

    // Moves on to the eligibility screen
    // check the terms and conditions link and click "Accept and start..."
    //
    // this click actually goes to the "terms and conditions" link which
    // brings up a modal
    cy.get('label[for=check-start-new-submission]').click();
    cy.get('.usa-button').contains('Accept and start').click();
    cy.url().should('match', /\/report_submission\/eligibility\/$/);

    // Completes the eligibility screen
    testValidEligibility();

    // Now the auditee info screen
    testValidAuditeeInfo();

    // Now the accessandsubmission screen
    testValidAccess();

    // Fill out the general info form
    testValidGeneralInfo();

    // Fill out the audit report package form, and upload its associated PDF
    // testAuditReportPackage();

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
    
    // Complete the audit information form
    cy.get(".usa-link").contains("Audit Information form").click();
    testAuditInformationForm();

    cy.get(".usa-link").contains("Pre-submission validation").click();
    testCrossValidation();

    // Auditor certification
    cy.get(".usa-link").contains("Auditor Certification").click();
    testAuditorCertification();

    // Auditee certification
    cy.url().then(url => {
      // Grab the report ID from the URL
      const reportId = url.split('/').pop();

      testLogoutGov();

      // Login as Auditee
      testLoginGovLogin(
        LOGIN_TEST_EMAIL_AUDITEE,
        LOGIN_TEST_PASSWORD_AUDITEE,
        LOGIN_TEST_OTP_SECRET_AUDITEE
      );

      cy.visit(`/audit/submission-progress/${reportId}`);

      cy.get(".usa-link").contains("Auditee Certification").click();
      testAuditeeCertification();
    })

    // Uncomment this block when ready to implement the certification steps.
    /*
    // Finally, submit for processing.
    cy.get(".usa-link").contains("Submit to the FAC for processing").click();
    // This will probably take you back to the homepage, where the audit is now oof status "submitted".
    */
  });
});
