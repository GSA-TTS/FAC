import { testCrossValidation } from '../support/cross-validation.js';
import { testLoginGovLogin } from '../support/login-gov.js';
import { testValidAccess } from '../support/check-access.js';
import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';
import { testValidGeneralInfo } from '../support/general-info.js';
import { testWorkbookFederalAwards,
         testWorkbookFindingsUniformGuidance,
         testWorkbookFindingsText,
         testWorkbookCorrectiveActionPlan,
         testWorkbookAdditionalUEIs } from '../support/workbook-uploads.js'

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

    // Upload all the workbooks
    cy.get(".usa-link").contains("Federal Awards").click();
    testWorkbookFederalAwards(false);  // don't intercept

    cy.get(".usa-link").contains("Federal Awards Audit Findings").click();
    testWorkbookFindingsUniformGuidance(false);  // don't intercept

    cy.get(".usa-link").contains("Federal Awards Audit Findings Text").click();
    testWorkbookFindingsText(false);  // don't intercept

    cy.get(".usa-link").contains("Corrective Action Plan").click();
    testWorkbookCorrectiveActionPlan(false);  // don't intercept

    cy.get(".usa-link").contains("Additional UEIs").click();
    testWorkbookAdditionalUEIs(false);  // don't intercept

    cy.get(".usa-link").contains("Pre-submission validation").click();
    testCrossValidation();

    // Uncomment this block when ready to implement the certification steps.
    /*

    // These aren't enabled because the previous steps didn't actually upload anything. Our upload responses are mocked.
    // First step, pre-validation.
    cy.get(".usa-link").contains("Pre-submission validation").click();
    cy.url().should('match', /\/audit\/ready-for-certification\/[0-9A-Z]{17}/);
    // Mock a prositive response on validation, then it comes back to the checklist

    // Second, auditor certification
    cy.get(".usa-link").contains("Auditor Certification").click();
    // Two pages:
    // 1. Click all the checkboxes to agree, submit and got to page 2
    // 2. Sign and date, submit and go back to checklist

    // Third, auditee certification
    cy.get(".usa-link").contains("Auditee Certification").click();
    // The same as auditor certification, with different checkboxes.

    // Finally, submit for processing.
    cy.get(".usa-link").contains("Submit to the FAC for processing").click();
    // This will probably take you back to the homepage, where the audit is now oof status "submitted".

    */
  });
});
