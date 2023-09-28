// reusable code for the accessandsubmission page
const accessFields = [
  '#certifying_auditee_contact_fullname', '#certifying_auditee_contact_email', '#certifying_auditee_contact_re_email',
  '#certifying_auditor_contact_fullname', '#certifying_auditor_contact_email', '#certifying_auditor_contact_re_email',
  '#auditee_contacts_fullname', '#auditee_contacts_email', '#auditee_contacts_re_email',
  '#auditor_contacts_fullname', '#auditor_contacts_email', '#auditor_contacts_re_email',
];

export function addValidInfo(field) {
  const fieldType = field.split('_').pop();
  const email = field.includes('auditee') ? Cypress.env('LOGIN_TEST_EMAIL_AUDITEE') : Cypress.env('LOGIN_TEST_EMAIL');

  cy.get(field)
    .clear()
    .type(fieldType === 'email' ? email : 'Percy A. Person')
    .blur();
}

export function testValidAccess() {
  cy.wrap(accessFields).each((field) => {
    addValidInfo(field);
  });
  cy.get('.usa-button').contains('Save and create').click();
  cy.url().should('contains', '/report_submission/general-information/');
}
