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
    cy.get(".usa-link").contains("Federal Awards workbook").click();
    testWorkbookFederalAwards(false);  // don't intercept

    cy.get(".usa-link").contains("Audit Findings workbook").click();
    testWorkbookFindingsUniformGuidance(false);  // don't intercept

    cy.get(".usa-link").contains("Audit Findings Text workbook").click();
    testWorkbookFindingsText(false);  // don't intercept

    cy.get(".usa-link").contains("Corrective Action Plan (CAP) workbook").click();
    testWorkbookCorrectiveActionPlan(false);  // don't intercept

    cy.get(".usa-link").contains("Additional UEIs workbook").click();
    testWorkbookAdditionalUEIs(false);  // don't intercept
  });
});
