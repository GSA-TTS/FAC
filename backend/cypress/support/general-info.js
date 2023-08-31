// reusable code for filling out a valid general info form

export function testValidGeneralInfo() {
	//auditee info
	cy.get('label[for=single-audit]').click();
	cy.get('label[for=audit-period-annual]').click();

  // these both have dates from a previous screen
	//cy.get('#auditee_fiscal_period_start').type('05/08/2023');
	//cy.get('#auditee_fiscal_period_end').type('05/08/2024');
  // this has a name from the previous screen
	//cy.get('#auditee_name').type('Commonwealth of Virginia');
	cy.get('#auditee_address_line_1').type('1111 E Broad ST');
	cy.get('#auditee_city').type('Richmond');
	cy.get('#auditee_state').type('VA');
	cy.get('#auditee_zip').type('23219');
  // there should already be a UEI in this box
	// cy.get('#auditee_uei').type('CMBSGK6P7BE1');
	cy.get('label[for=multiple-ueis-yes]').click();
	cy.get('#ein').type('546000173');
	cy.get('label[for=ein_not_an_ssn_attestation]').click();
	cy.get('label[for=multiple-eins-no]').click();
	cy.get('#auditee_contact_name').type('John Doe');
	cy.get('#auditee_contact_title').type('Keymaster');
	cy.get('#auditee_phone').type('5558675309');
	cy.get('#auditee_email').type('va@test');

	//auditor info
	cy.get('#auditor_firm_name').type('House of Audit');
	cy.get('#auditor_country').type('USA');
	cy.get('#auditor_address_line_1').type('123 Around the corner');
	cy.get('#auditor_city').type('Centreville');
	cy.get('#auditor_state').type('VA');
	cy.get('#auditor_zip').type('20121');
	cy.get('#auditor_ein').type('987654321');
	cy.get('#auditor_contact_name').type('Jane Doe');
	cy.get('#auditor_contact_title').type('Auditor');
	cy.get('#auditor_phone').type('5555555555');
	cy.get('#auditor_email').type('qualified.human.accountant@auditor');
	cy.get('label[for=secondary_auditors-yes]').click();

	cy.get('#continue').click();

	cy.url().should('match', /\/audit\/submission-progress\/[0-9A-Z]{17}$/);
};
