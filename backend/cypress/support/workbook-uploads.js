// re-usable code for workbook uploads

// testWorkbookUpload('/audit/excel/federal-awards-expended/*', '#file-input-federal-awards-xlsx', 'federal-awards-expended-UPDATE.xlsx')
// assumes you are on the appropriate upload page already
function testWorkbookUpload(interceptUrl, uploadSelector, filename, will_intercept = true) {
  if (will_intercept) {
    cy.intercept('POST', interceptUrl + '*', (req) => {
      req.reply({ fixture: 'success-res.json' });
    }).as('uploadSuccess');
  } else {
    cy.intercept('POST', interceptUrl + '*').as('uploadSuccess');
  }

  cy.get(uploadSelector).attachFile(filename);
  // Upload url (POST /audit/excel/workbookname) returns a redirect to "/" on successful upload. So, 302.
  cy.wait('@uploadSuccess').should(({request, response}) => {
    expect(response.statusCode, 'Response status code').to.equal(302);
  });
  cy.get('#info_box', { timeout: 10000 })
    .should(
      'have.text',
      'File successfully validated! Your work has been saved.'
    );

  cy.get('#continue').click();
  cy.url().should('match', /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
}

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
