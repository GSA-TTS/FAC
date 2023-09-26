export function testAuditeeCertification() {
    // 1. Click all the checkboxes to agree, submit and go to page 2
    cy.get('label[for=has_no_PII]').click();
    cy.get('label[for=has_no_BII]').click();
    cy.get('label[for=meets_2CFR_specifications]').click();
    cy.get('label[for=is_2CFR_compliant]').click();
    cy.get('label[for=is_complete_and_accurate]').click();
    cy.get('label[for=has_engaged_auditor]').click();
    cy.get('label[for=is_issued_and_signed]').click();
    cy.get('label[for=is_FAC_releasable]').click();
    cy.get('.usa-button').contains('Agree to auditee certification').click();
  
    // 2. Sign and date, submit and go back to checklist
    cy.get('#auditee_name').type('John Doe');
    cy.get('#auditee_title').type('Auditee');
    cy.get('#auditee_certification_date_signed').type("01/01/2022");
    cy.get('.usa-button').contains('Agree to auditee certification').click();
  }