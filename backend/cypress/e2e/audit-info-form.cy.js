/*
  Tests for the audit information form page. 
  INCOMPLETE. Awaiting login.gov to work with Cypress.
*/
describe('Audit Information Form', () => {
  beforeEach(() => {
    cy.visit('/audit/audit-info/2022JAN0001000006');
  });

  function answerAllQuestions() {
    // Select everything for the GAAP multiple choice checkboxes.
    cy.get('[id^=gaap_results--]').each((item) => {
      cy.get(item).click();
    });
    // Answer 'Yes' to all Yes/No questions.
    cy.get('[id$=--true]').each((item) => {
      cy.get(item).click();
    });
    // Enter 750000 into the dollar theshold number field.
    cy.get('#dollar_threshold').type('750000');
    cy.get('#dollar_threshold').blur();
    // Select 0 and 1 for the multiple select agencies field.
    cy.get('#agencies').select(['00', '01']);
    cy.get('#agencies').blur();
  }

  it('Page loads successfully', () => {
    cy.url().should('include', '/audit-info/');
  });

  it('Submit button is disabled on empty form', () => {
    cy.get('continue').should('be.disabled');
  });

  it.only('Submit button is enabled after filling out all fields.', () => {
    answerAllQuestions();
    cy.get('continue').should('be.enabled');
  });

  it.only('Sucessful submit redirects to the audit checklist.', () => {
    answerAllQuestions();
    cy.get('continue').should('be.enabled').click();
    cy.url().should('include', '/submission-progress/');
  });

  describe('Number Field', () => {
    it('Cannot type non-int values (only allows numbers and [+-.e])', () => {
      cy.get('#dollar_threshold').clear();
      cy.get('#dollar_threshold').type(
        `abcdfghigklmnopqrstuvwxyz=[];',/!@#$%^&*()_{}|:"<>?~`
      );
      cy.get('#dollar_threshold').should('have.value', '');
    });

    it('Negative values are disallowed', () => {
      answerAllQuestions(); // Enable submit button.
      cy.get('#dollar_threshold').clear();
      cy.get('#dollar_threshold').type(`-2`);
      cy.get('#continue').click();
      cy.url().should('include', '/audit-info/');
    });

    it('Decimal values are disallowed', () => {
      answerAllQuestions(); // Enable submit button.
      cy.get('#dollar_threshold').clear();
      cy.get('#dollar_threshold').type(`777.77`);
      cy.get('#continue').click();
      cy.url().should('include', '/audit-info/');
    });
  });
});
