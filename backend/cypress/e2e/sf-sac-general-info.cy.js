describe('Create New Audit', () => {
  const CONTINUE_BUTTON_TEXT = 'Save & continue to next section';

  beforeEach(() => {
    cy.fixture('sac-report').as('sacReport');
    cy.get('@sacReport').then((report) => {
      cy.intercept('GET', '/sac/edit/*', report).as('setSacInfo');
    });
  });

  before(() => {
    cy.visit('/audit/submission?reportId=2022ZEL0001000006');
  });

  describe('A Blank Form', () => {
    it('does not show any errors initially', () => {
      cy.get('[class*=--error]').should('have.length', 0);
    });

    it('marks empty responses as invalid', () => {
      cy.get('#general-info input:invalid').should('have.length', 10);
    });

    it('will not submit', () => {
      cy.get('#general-info').invoke('submit', (e) => {
        e.preventDefault();
        throw new Error('Form was submitted'); // The test will fail if this error is thrown
      });

      cy.get('.usa-button').contains(CONTINUE_BUTTON_TEXT).click();
    });

    it('should disable the "Continue" button when validation fails', () => {
      cy.get('button').contains(CONTINUE_BUTTON_TEXT).should('be.disabled');
    });
  });

  describe('Validation', () => {
    it('should display error messages for invalid entities', () => {
      cy.get('.usa-error-message:visible').should('have.length', 18);
    });

    it('should remove errors when valid properties are checked', () => {
      // This needs to be a click on the label rather than a
      // check on the input itself because of the CSS magic
      // USWDS does to make the fancy radio buttons

      // Click twice to trigger the blur event,
      // or in the case of a checkbox, click the `next` element

      cy.get('label[for=single-audit]').click();
      cy.get('label[for=single-audit]').click();

      cy.get('label[for=audit-period-annual]').click();
      cy.get('label[for=audit-period-annual]').click();

      cy.get('label[for=ein_not_an_ssn_attestation]').click();

      cy.get('label[for=multiple-eins-yes]').click();
      cy.get('label[for=multiple-eins-yes]').click();

      cy.get('label[for=multiple-ueis-yes]').click();
      cy.get('label[for=multiple-ueis-yes]').click();

      cy.get('label[for=auditor_ein_not_an_ssn_attestation]').click();

      cy.get('.radio.usa-form-group--error').should('have.length', 0);
      cy.get('.usa-checkbox.usa-form-group--error').should('have.length', 0);
    });

    it('should remove errors when text fields have text in them', () => {
      cy.get('.usa-input:not(.radio):not(.usa-checkbox):not([disabled])').each(
        (i) => {
          cy.get(i).type('asdf');
        }
      );
      cy.get('label[for=auditor_phone]').click();
      cy.get('.usa-checkbox.usa-form-group--error').should('have.length', 0);
    });
  });

  describe('Populating the form with existing data', () => {
    it('should populate the report ID', () => {
      cy.visit('/audit/submission?reportId=2022ZEL0001000006');
      cy.wait('@setSacInfo').then(() => {
        cy.get('@sacReport').then((report) => {
          cy.get('[data-test-id="auditeeName"]').should(
            'have.text',
            report.auditee_name
          );
          cy.get('[data-test-id="reportId"]').should(
            'have.text',
            report.report_id
          );
          cy.get('#auditee_name').should('have.value', report.auditee_name);
          cy.get('#auditee_uei').should('have.value', report.auditee_uei);
          cy.get('#auditee_email').children('option').should('have.length', 3);
        });
      });
    });

    it('should remove errors when select fields have values', () => {
      cy.get('#auditee_email').select('a@a.com');
      cy.get('#auditor_email').select('c@c.com');
      cy.get('.usa-form-group--error').should('have.length', 0);
    });

    it('should enable the "Continue" button when entities are fixed', () => {
      cy.get('button').contains(CONTINUE_BUTTON_TEXT).should('not.be.disabled');
    });
  });
});
