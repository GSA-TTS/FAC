import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';

describe('Create New Audit', () => {

  beforeEach(() => {
    // contents of session are only called once
    cy.session('loginSession', () => {
      cy.visit('/')
      cy.login();

      // submitting accessandsubmission can't succeed unless we fill in some
      // of the previous pages
      cy.visit('/report_submission/eligibility/')
      testValidEligibility();
      testValidAuditeeInfo();
    });
    cy.visit('/report_submission/accessandsubmission/');
  });

  function addValidEmail(field) {
    cy.get(field)
      .clear()
      .type('test.address-with+features@test.gsa.gov')
      .blur();
  }

  describe('A Blank Form', () => {
    it('marks empty responses as invalid', () => {
      cy.get('#grant-access input:invalid').should('have.length', 8);
    });

    it('will not submit', () => {
      cy.get('form#grant-access').invoke('submit', (e) => {
        e.preventDefault();
        throw new Error('Form was submitted'); // The test will fail if this error is thrown
      });

      cy.get('button').contains('Create').click();
    });
  });

  describe('Validation', () => {
    it('does not show any errors initially', () => {
      cy.get('[class*=--error]').should('have.length', 0);
    });

    describe('Auditee certifying official', () => {
      describe('Email Address', () => {
        it('should display an error message when left blank', () => {
          cy.get('#certifying_auditee_contact_email').click().blur();
          cy.get('#certifying_auditee_contact_email-not-null').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#certifying_auditee_contact_email').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          cy.get('#certifying_auditee_contact_email')
            .clear()
            .type('A Name')
            .blur();
          cy.get('#certifying_auditee_contact_email-not-null').should(
            'not.be.visible'
          );
        });

        it('should display an error message when entry is invalid', () => {
          cy.get('#certifying_auditee_contact_email').click().blur();
          cy.get('#certifying_auditee_contact_email-error-message').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are invalid', () => {
          cy.get('#certifying_auditee_contact_email').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when valid input is supplied', () => {
          addValidEmail('#certifying_auditee_contact_email');
          cy.get('#certifying_auditee_contact_email-error-message').should(
            'not.be.visible'
          );
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidEmail('#certifying_auditee_contact_email');
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });

      describe('Email Address Confirmation', () => {
        it('should display an error message when input does not match email field', () => {
          addValidEmail('#certifying_auditee_contact_email');
          cy.get('#certifying_auditee_contact_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#certifying_auditee_contact_re_email-must-match').should(
            'be.visible'
          );
        });

        it('should remove the error message when input matches email field', () => {
          addValidEmail('#certifying_auditee_contact_email');
          addValidEmail('#certifying_auditee_contact_re_email');
          cy.get('#certifying_auditee_contact_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });
    });

    describe('Auditor certifying official', () => {
      describe('Email Address', () => {
        it('should display an error message when left blank', () => {
          cy.get('#certifying_auditor_contact_email').click().blur();
          cy.get('#certifying_auditor_contact_email-not-null').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#certifying_auditor_contact_email').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          cy.get('#certifying_auditor_contact_email')
            .clear()
            .type('A Name')
            .blur();
          cy.get('#certifying_auditor_contact_email-not-null').should(
            'not.be.visible'
          );
        });

        it('should display an error message when entry is invalid', () => {
          cy.get('#certifying_auditor_contact_email')
            .clear()
            .type('A Name')
            .blur();
          cy.get('#certifying_auditor_contact_email').click().blur();
          cy.get('#certifying_auditor_contact_email-email').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are invalid', () => {
          cy.get('#certifying_auditor_contact_email').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when valid input is supplied', () => {
          addValidEmail('#certifying_auditor_contact_email')
          cy.get('#certifying_auditor_contact_email-email').should(
            'not.be.visible'
          );
        });

        it('should enable the "Create" button when entities are fixed', () => {
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });

      describe('Email Address Confirmation', () => {
        it('should display an error message when input does not match email field', () => {
          addValidEmail('#certifying_auditor_contact_email')
          cy.get('#certifying_auditor_contact_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#certifying_auditor_contact_re_email-must-match').should(
            'be.visible'
          );
        });

        it('should remove the error message when input matches email field', () => {
          addValidEmail('#certifying_auditor_contact_email')
          addValidEmail('#certifying_auditor_contact_re_email')

          cy.get('#certifying_auditor_contact_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });
    });

    describe('Auditee contacts', () => {
      describe('Email Address', () => {
        it('should display an error message when left blank', () => {
          cy.get('#auditee_contacts_email').click().blur();
          cy.get('#auditee_contacts_email-not-null').should('be.visible');
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#auditee_contacts_email').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          cy.get('#auditee_contacts_email').clear().type('A Name').blur();
          cy.get('#auditee_contacts_email-not-null').should('not.be.visible');
        });

        it('should display an error message when entry is invalid', () => {
          cy.get('#auditee_contacts_email').clear().type('A Name').blur();
          cy.get('#auditee_contacts_email-email').should('be.visible');
        });

        it('should remove the error message when valid input is supplied', () => {
          addValidEmail('#auditee_contacts_email')
          cy.get('#auditee_contacts_email-email').should('not.be.visible');
        });
      });

      describe('Email Address Confirmation', () => {
        it('should display an error message when input does not match email field', () => {
          addValidEmail('#auditee_contacts_email')

          cy.get('#auditee_contacts_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#auditee_contacts_re_email-must-match').should('be.visible');
        });

        it('should remove the error message when input matches email field', () => {
          addValidEmail('#auditee_contacts_email')
          addValidEmail('#auditee_contacts_re_email')

          cy.get('#auditee_contacts_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });

      it('should allow adding new contact fields', () => {
        cy.get('.auditee_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 2);
        });
      });

      it('should allow deleting additional contact fields', () => {
        cy.get('.auditee_contacts').within(() => {
          cy.get('button').click();
        });

        cy.get('.auditee_contacts .delete-contact').click();
        cy.get('.auditee_contacts .grid-row').should('have.length', 1);
      });

      it('should be able to add contact and contact info to new inputs', () => {
        cy.get('.auditee_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 2);
          cy.get('input[id*="auditee_contacts_email"]')
            .eq(1)
            .clear()
            .type('test.address-with+features@test.gsa.gov');
          cy.get('input[id*="auditee_contacts_re_email"]')
            .eq(1)
            .clear()
            .type('test.address-with+features@test.gsa.gov');
        });
      });
    });

    describe('Auditor contacts', () => {
      describe('Email Address', () => {
        it('should display an error message when left blank', () => {
          cy.get('#auditor_contacts_email').click().blur();
          cy.get('#auditor_contacts_email-not-null').should('be.visible');
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#auditor_contacts_email').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          cy.get('#auditor_contacts_email').clear().type('A Name').blur();
          cy.get('#auditor_contacts_email-not-null').should('not.be.visible');
        });

        it('should display an error message when entry is invalid', () => {
          cy.get('#auditor_contacts_email').clear().type('A Name').blur();
          cy.get('#auditor_contacts_email-email').should('be.visible');
        });

        it('should disable the submit button when fields are invalid', () => {
          cy.get('#auditor_contacts_email').clear().type('A Name').blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when valid input is supplied', () => {
          addValidEmail('#auditor_contacts_email')
          cy.get('#auditor_contacts_email-email').should('not.be.visible');
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidEmail('#auditor_contacts_email')
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });

      describe('Email Address Confirmation', () => {
        it('should display an error message when input does not match email field', () => {
          addValidEmail('#auditor_contacts_email')

          cy.get('#auditor_contacts_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#auditor_contacts_re_email-must-match').should('be.visible');
        });

        it('should remove the error message when input matches email field', () => {
          addValidEmail('#auditor_contacts_email')
          addValidEmail('#auditor_contacts_re_email')

          cy.get('#auditor_contacts_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });

      it('should allow adding new contact fields', () => {
        cy.get('.auditor_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 2);
        });
      });

      it('should allow deleting additional contact fields', () => {
        cy.get('.auditor_contacts').within(() => {
          cy.get('button').click();
        });

        cy.get('.auditor_contacts .delete-contact').click();
        cy.get('.auditor_contacts .grid-row').should('have.length', 1);
      });

      it('should be able to add contact and contact info to new inputs', () => {
        cy.get('.auditor_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 2);
          cy.get('input[id*="auditor_contacts_email"]')
            .eq(1)
            .clear()
            .type('test.address-with+features@test.gsa.gov');
          cy.get('input[id*="auditor_contacts_re_email"]')
            .eq(1)
            .clear()
            .type('test.address-with+features@test.gsa.gov');
        });
      });
    });

    function completeFormWithValidInfo() {
      [
        '#certifying_auditee_contact_email', '#certifying_auditee_contact_re_email',
        '#certifying_auditor_contact_email', '#certifying_auditor_contact_re_email',
        '#auditee_contacts_email', '#auditee_contacts_re_email',
        '#auditor_contacts_email', '#auditor_contacts_re_email' 
      ].forEach(field => addValidEmail(field))
    }

    it('should proceed to the next step after successful submission', () => {
      completeFormWithValidInfo();
      cy.get('.usa-button').contains('Create').click();
      cy.url().should('contains', '/report_submission/general-information/');
    });
  });

  it('Canceling an audit submission returns to the home page', () => {
    cy.get('.usa-button').contains('Cancel').click();
    cy.get('.usa-button').contains('OK').click();
    cy.url().should('include', '/audit/');
  });
});
