/*
  Re-useable code for silling out the audit information form.
*/
export function testAuditInformationForm() {
  // Select everything for the GAAP multiple choice checkboxes.
  // Will pop the three conditional non-GAAP questions.
  cy.get('[id^=gaap_results--]').each((item) => {
    cy.get(item).click({ force: true });
  });

  // Select everything for question i
  cy.get('[id^=sp_framework_basis--]').each((item) => {
    cy.get(item).click({ force: true });
  });

  // Question ii is a true/false, and is covered below

  // Select everything for question iii
  cy.get('[id^=sp_framework_opinions--]').each((item) => {
    cy.get(item).click({ force: true });
  });

  // Answer 'Yes' to all Yes/No questions.
  cy.get('[id$=--true]').each((item) => {
    cy.get(item).click({ force: true });
  });

  // Enter 750000 into the dollar theshold number field.
  cy.get('#dollar_threshold').type('750000');
  cy.get('#dollar_threshold').blur();

  // Select 0 and 1 for the multiple select agencies field.
  cy.get('#agencies').select(['00', '01']);
  cy.get('#agencies').blur();

  cy.get('.usa-button').contains('Save and continue').click({ force: true });

  cy.url().should(
    'match',
    /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/
  );
}
