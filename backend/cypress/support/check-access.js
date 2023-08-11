// reusable code for the accessandsubmission page

export function addValidEmail(field) {
  cy.get(field)
    .clear()
    .type('test.address-with+features@test.gsa.gov')
    .blur();
}

export function addFullName(field) {
  cy.get(field)
    .clear()
    .type('Real Full Name')
    .blur();
}

function completeFormWithValidEmail() {
  [
    '#certifying_auditee_contact_email', '#certifying_auditee_contact_re_email',
    '#certifying_auditor_contact_email', '#certifying_auditor_contact_re_email',
    '#auditee_contacts_email', '#auditee_contacts_re_email',
    '#auditor_contacts_email', '#auditor_contacts_re_email'
  ].forEach(field => addValidEmail(field))
}

function completeFormWithFullnames() {
  [
    '#certifying_auditee_contact_fullname',
    '#certifying_auditor_contact_fullname',
    '#auditee_contacts_fullname',
    '#auditor_contacts_fullname',
  ].forEach(field => addFullName(field))
}

export function testValidAccess() {
  completeFormWithValidEmail();
  completeFormWithFullnames();
  cy.get('.usa-button').contains('Create').click();
  cy.url().should('contains', '/report_submission/general-information/');
}
