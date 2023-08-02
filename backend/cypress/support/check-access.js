// reusable code for the accessandsubmission page

export function addValidEmail(field) {
  cy.get(field)
    .clear()
    .type('test.address-with+features@test.gsa.gov')
    .blur();
}

function completeFormWithValidInfo() {
  [
    '#certifying_auditee_contact_email', '#certifying_auditee_contact_re_email',
    '#certifying_auditor_contact_email', '#certifying_auditor_contact_re_email',
    '#auditee_contacts_email', '#auditee_contacts_re_email',
    '#auditor_contacts_email', '#auditor_contacts_re_email' 
  ].forEach(field => addValidEmail(field))
}

export function testValidAccess() {
  completeFormWithValidInfo();
  cy.get('.usa-button').contains('Create').click();
  cy.url().should('contains', '/report_submission/general-information/');
}
