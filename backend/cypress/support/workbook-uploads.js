// re-usable code for workbook uploads

// testWorkbookUpload('/audit/excel/federal-awards-expended/*', '#file-input-federal-awards-xlsx', 'federal-awards-expended-UPDATE.xlsx')
// assumes you are on the appropriate upload page already
function testWorkbookUpload(interceptUrl, uploadSelector, filename, intercept = true) {
    cy.intercept(interceptUrl + '*', (req) => {
      if (intercept) {
        // return a success fixture
        req.reply({ fixture: 'success-res.json' });
      } else {
        // with no intercept, don't intervene
        req.continue();
      }
    }).as('uploadSuccess');
  cy.get(uploadSelector).attachFile(filename);
  cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200);
  cy.wait(2000)
    .get('#info_box')
    .should(
      'have.text',
      'File successfully validated! Your work has been saved.'
    );
  cy.get('#continue').click();
  cy.url().should('match', /\/audit\/submission-progress\/[0-9A-Z]{17}/);
}

export function testWorkbookFederalAwards(intercept = true) {
  testWorkbookUpload(
    '/audit/excel/federal-awards-expended/*',
    '#file-input-federal-awards-xlsx',
    'federal-awards-expended-PASS.xlsx'
  );
}

export function testWorkbookFindingsUniformGuidance(intercept = true) {
  testWorkbookUpload(
    '/audit/excel/findings-uniform-guidance/',
    '#file-input-audit-findings-xlsx',
    'findings-uniform-guidance-UPDATE.xlsx'
  )
}

export function testWorkbookFindingsText(intercept = true) {
  testWorkbookUpload(
    '/audit/excel/findings-text/',
    '#file-input-audit-findings-text-xlsx',
    'findings-text-UPDATE.xlsx'
  )
}

export function testWorkbookCorrectiveActionPlan(intercept = true) {
  testWorkbookUpload(
    '/audit/excel/corrective-action-plan/',
    '#file-input-CAP-xlsx',
    'corrective-action-plan-UPDATE.xlsx'
  )
}

export function testWorkbookAdditionalUEIs(intercept = true) {
  testWorkbookUpload(
    '/audit/excel/additional-ueis/',
    '#file-input-additional-ueis-xlsx',
    'additional-ueis.xlsx'
  )
}
