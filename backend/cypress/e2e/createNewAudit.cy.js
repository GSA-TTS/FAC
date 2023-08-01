import { testValidGeneralInfo } from '../support/general-info.js';

describe('Create new audit', () => {
    //const reportTestId = '2023MAY0001000001';

    before(() => {
      cy.visit('http://localhost:8000/report_submission/eligibility/');
    });
        //got the page elements from Cypress Desktop
        it('Fills out the Submission criteria check and clicks items', () => {
            cy.get(':nth-child(3) > :nth-child(2) > .usa-radio__label').click();
            cy.get(':nth-child(4) > :nth-child(2) > .usa-radio__label').click();
            cy.get(':nth-child(5) > :nth-child(2) > .usa-radio__label').click();
            cy.get('#continue').click();
            cy.url().should('contain', '/report_submission/auditeeinfo/');
        });

        it('Fills out the Auditee Information', () => {
            cy.get('#auditee_uei').type('CMBSGK6P7BE1');
            cy.get('#auditee_uei-btn').click(); 
            cy.get('auditee_fiscal_period_start').type('05/08/2023');
            cy.get('auditee_fiscal_period_end').type('05/08/2024');
            cy.get('#continue').click();
            cy.url().should('contain', '/report_submission/accessandsubmission/');
});

        it('Fills out the Audit submission access', () => {
            cy.get('#certifying_auditee_contact_email').type('va@test');
            cy.get('#certifying_auditor_contact_email').type('qualified.human.accountant@auditor.com');
            cy.get('#auditee_contacts_email').type('a@a.com');
            cy.get('#auditor_contacts_email').type('c@c.com');
            cy.get('#create').click();
            cy.url().should('contain', '/report_submission/general-information/2023MAY0001000001');
        });

        it('Fills out the General Information Form', () => {
					testValidGeneralInfo();
				});
});
