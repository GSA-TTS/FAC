// re-usable code for workbook uploads

// testWorkbookUpload('/audit/excel/federal-awards-expended/*', '#file-input-federal-awards-xlsx', 'federal-awards-expended-UPDATE.xlsx')
// assumes you are on the appropriate upload page already
function testWorkbookUpload(interceptUrl, uploadSelector, filename, will_intercept = true) {
    cy.intercept(interceptUrl + '*', (req) => {
      if (will_intercept) {
        // return a success fixture
        req.reply({ fixture: 'success-res.json' });
      } else {
        // with no intercept, don't intervene
        req.continue();
      }
    }).as('uploadSuccess');
  cy.get(uploadSelector).attachFile(filename);
  // Upload url (POST /audit/excel/workbookname) returns a redirect to "/" on successful upload. So, 302.
  cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 302);
  cy.get('#info_box')
    .should(
      'have.text',
      'File successfully validated! Your work has been saved.'
    );

  cy.get('#continue').click();
  cy.url().should('match', /\/audit\/submission-progress\/[0-9A-Z]{17}/);
}

export function testWorkbookFederalAwards(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/federal-awards-expended/*',
    '#file-input-federal-awards-xlsx',
    `test_workbooks/${workbookDirName}/federal-awards-workbook.xlsx`,
    will_intercept
  );
}

export function testWorkbookNotesToSEFA(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/notes-to-sefa/*',
    '#file-input-notes-to-sefa-xlsx',
    `test_workbooks/${workbookDirName}/notes-to-sefa-workbook.xlsx`,
    will_intercept
  );
}

export function testWorkbookFindingsUniformGuidance(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/findings-uniform-guidance/',
    '#file-input-audit-findings-xlsx',
    `test_workbooks/${workbookDirName}/federal-awards-audit-findings-workbook.xlsx`,
    will_intercept
  )
}

export function testWorkbookFindingsText(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/findings-text/',
    '#file-input-audit-findings-text-xlsx',
    `test_workbooks/${workbookDirName}/audit-findings-text-workbook.xlsx`,
    will_intercept
  )
}

export function testWorkbookCorrectiveActionPlan(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/corrective-action-plan/',
    '#file-input-cap-xlsx',
    `test_workbooks/${workbookDirName}/corrective-action-plan-workbook.xlsx`,
    will_intercept
  )
}

export function testWorkbookAdditionalUEIs(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/additional-ueis/',
    '#file-input-additional-ueis-xlsx',
    `test_workbooks/${workbookDirName}/additional-ueis-workbook.xlsx`,
    will_intercept
  )
}

export function testWorkbookSecondaryAuditors(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/secondary-auditors/',
    '#file-input-secondary-auditors-xlsx',
    `test_workbooks/${workbookDirName}/secondary-auditors-workbook.xlsx`,
    will_intercept
  )
}

export function testWorkbookAdditionalEINs(workbookDirName, will_intercept = true) {
  testWorkbookUpload(
    '/audit/excel/additional-eins/',
    '#file-input-additional-eins-xlsx',
    `test_workbooks/${workbookDirName}/additional-eins-workbook.xlsx`,
    will_intercept
  )
}
