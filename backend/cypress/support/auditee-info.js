// re-usable code for testing the Auditee Info form

function fillAuditeeFields({ uei, start, end }) {
  cy.get('#auditee_uei').clear();
  cy.get('#auditee_uei').type(uei);
  cy.get('#auditee_uei').blur();

  cy.get('#auditee_fiscal_period_start').clear();
  cy.get('#auditee_fiscal_period_start').type(start);
  cy.get('#auditee_fiscal_period_start').blur();

  cy.get('#auditee_fiscal_period_end').clear();
  cy.get('#auditee_fiscal_period_end').type(end);
  cy.get('#auditee_fiscal_period_end').blur();
}

function clickValidateUEI() {
  cy.get('#continue').should('not.be.disabled');
  cy.get('#continue').click();
}

function waitForUEIModalReady() {
  // modal is open
  cy.get('#uei-search-result').should('have.class', 'is-visible');
  // loading spinner removed 
  cy.get('#uei-search-result').should('not.have.class', 'loading');

  // primary button has been populated by populateModal()
  cy.get('#uei-search-result .usa-modal__footer button.primary')
    .invoke('text')
    .then((t) => t.trim())
    .should('match', /^(Continue|Yes, continue)$/);
}

function clickUEIModalPrimary() {
  // Click even if Cypress thinks it's not visible due to modal CSS timing
  cy.get('#uei-search-result .usa-modal__footer button.primary')
    .click({ force: true });
}

export function testValidAuditeeInfo() {
  cy.intercept('POST', '/api/sac/ueivalidation', {
    fixture: 'sam-gov-api-mock.json',
  }).as('uei_check');

  fillAuditeeFields({
    uei: 'D7A4J33FUMJ1',
    start: '01/01/2023',
    end: '12/31/2023',
  });

  clickValidateUEI();
  cy.wait('@uei_check');

  waitForUEIModalReady();
  clickUEIModalPrimary();

  cy.url().should('match', /\/report_submission\/eligibility\/$/);
}

export function testDuplicateAuditeeInfo() {
  cy.intercept('POST', '/api/sac/ueivalidation', {
    fixture: 'uei-duplicate.json',
  }).as('uei_check_duplicate');

  fillAuditeeFields({
    uei: 'LZGKJ22EF7B5',
    start: '01/01/2023',
    end: '12/31/2023',
  });

  clickValidateUEI();
  cy.wait('@uei_check_duplicate');

  waitForUEIModalReady();

  cy.contains('Are you sure you want to start a new submission?');
  cy.contains('2023-12-GSAFAC-0000000001');
  cy.contains('2023-12-GSAFAC-0000000002');

  cy.get('#uei-search-result .usa-modal__footer button.primary')
    .should('have.text', 'Yes, continue');
  cy.get('#uei-search-result .usa-modal__footer button.primary').click();

  cy.url().should('match', /\/report_submission\/eligibility\/$/);
}