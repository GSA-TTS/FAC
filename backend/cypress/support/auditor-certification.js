export function testAuditorCertification() {
  // 1. Click all the checkboxes to agree, submit and go to page 2
  cy.get('label[for=is_OMB_limited]').click();
  cy.get('label[for=is_auditee_responsible]').click();
  cy.get('label[for=has_used_auditors_report]').click();
  cy.get('label[for=has_no_auditee_procedures]').click();
  cy.get('label[for=is_FAC_releasable]').click();
  cy.get('.usa-button').contains('Agree to auditor certification').click();

  // 2. Sign and date, submit and go back to checklist
  cy.get('#auditor_name').type('Jane Doe');
	cy.get('#auditor_title').type('Auditor');
  cy.get('#auditor_certification_date_signed').type("01/01/2022");
  cy.get('.usa-button').contains('Agree to auditor certification').click();
}
