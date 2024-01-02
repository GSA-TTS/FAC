/**
 * Tests an upload page. Assumes Cypress is on the appropriate upload page already.
 * 1. Define the requests to watch (intercepts)
 *   "uploadSuccess" - The file upload endpoint. On success, returns a 302 redirect to the homepage.
 *   "uploadRedirect" - The post-upload 302 redirects to the homepage '/', which then directs to '/audit/'.
 *   The first intercept cannot follow the redirect, so we watch for both requests. See https://github.com/cypress-io/cypress/issues/24700
 * 2. Attach a file to upload.
 * 3. Wait for the upload to complete by waiting for the requests to recieve proper responses.
 * 4. Ensure the information box updated correctly.
 * 5. Navigate through to the submission checklist.
 *
 * @param {string} interceptUrl The url for the file upload endpoint.
 * @param {string} uploadSelector The name of the fle upload input element.
 * @param {string} filename The path and name of the test file to upload.
 * @param {boolean} will_intercept Whether or not the function will mock the upload.
 * @return {null} No return value.
 */
function testWorkbookUpload(interceptUrl, uploadSelector, filename, will_intercept = true) {
  cy.intercept(interceptUrl + '*', (req) => {
    if (will_intercept) {
      req.reply({ fixture: 'success-res.json' });
    } else {
      req.continue();
    }
  }).as('uploadSuccess');
  cy.intercept('/audit/').as('uploadRedirect');

  cy.get(uploadSelector).attachFile(filename);

  cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 302);
  cy.wait('@uploadRedirect').its('response.statusCode').should('eq', 200);
  
  cy.get('#info_box')
    .should(
      'have.text',
      'File successfully validated! Your work has been saved.'
    );

  cy.get('#continue').click();
  cy.url().should('match', /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
}

/**
 * Calls testWorkbookUpload with the appropriate static names - upload URL, file input element name, and sample workbook. 
 * 
 * @param {boolean} will_intercept Whether or not testWorkbookUpload function will mock the upload. Defaults to true.
 * @return {null} No return value.
 */
export function testWorkbookFederalAwards(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/federal-awards-expended/*',
    '#file-input-federal-awards-xlsx',
    'test_workbooks/federal-awards-workbook.xlsx',
    will_intercept
  );
}

export function testWorkbookNotesToSEFA(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/notes-to-sefa/*',
    '#file-input-notes-to-sefa-xlsx',
    'test_workbooks/notes-to-sefa-workbook.xlsx',
    will_intercept
  );
}

export function testWorkbookFindingsUniformGuidance(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/findings-uniform-guidance/',
    '#file-input-audit-findings-xlsx',
    'test_workbooks/federal-awards-audit-findings-workbook.xlsx',
    will_intercept
  )
}

export function testWorkbookFindingsText(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/findings-text/',
    '#file-input-audit-findings-text-xlsx',
    'test_workbooks/audit-findings-text-workbook.xlsx',
    will_intercept
  )
}

export function testWorkbookCorrectiveActionPlan(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/corrective-action-plan/',
    '#file-input-cap-xlsx',
    'test_workbooks/corrective-action-plan-workbook.xlsx',
    will_intercept
  )
}

export function testWorkbookAdditionalUEIs(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/additional-ueis/',
    '#file-input-additional-ueis-xlsx',
    'test_workbooks/additional-ueis-workbook.xlsx',
    will_intercept
  )
}

export function testWorkbookSecondaryAuditors(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/secondary-auditors/',
    '#file-input-secondary-auditors-xlsx',
    'test_workbooks/secondary-auditors-workbook.xlsx',
    will_intercept
  )
}

export function testWorkbookAdditionalEINs(will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/additional-eins/',
    '#file-input-additional-eins-xlsx',
    'test_workbooks/additional-eins-workbook.xlsx',
    will_intercept
  )
}
