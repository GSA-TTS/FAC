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
            //auditee info
            cy.get('#single-audit').click();
            cy.get('#audit-period-annual').click();
            cy.get('#auditee_fiscal_period_start').type('05/08/2023');
            cy.get('#auditee_fiscal_period_end').type('05/08/2024');
            cy.get('#auditee_name').type('Commonwealth of Virginia');
            cy.get('#auditee_address_line_1').type('1111 E Broad ST');
            cy.get('#auditee_city').type('Richmond');
            cy.get('#auditee_state').type('VA');
            cy.get('#auditee_zip').type('23219');
            cy.get('#auditee_uei').type('CMBSGK6P7BE1');
            cy.get('#multiple-ueis-no').click();
            cy.get('#ein').type('5460001736');
            cy.get('#ein_not_an_ssn_attestation').click();
            cy.get('#multiple-eins-no').click();
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
            cy.get('#continue').click();
            cy.url().should('contain', '/report_submission/submission-progrss/2023MAY0001000001');
           });
});