import { testValidEligibility } from '../support/check-eligibility.js';
import { testValidAuditeeInfo } from '../support/auditee-info.js';
import { addValidInfo, testValidAccess } from '../support/check-access.js';

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

  describe('A Blank Form', () => {
    it('marks empty responses as invalid', () => {
      cy.get('#grant-access input:invalid').should('have.length', 12);
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
      describe('Full name', () => {
        it('should display an error message when left blank', () => {
          cy.get('#certifying_auditee_contact_fullname').click().blur();
          cy.get('#certifying_auditee_contact_fullname-not-null').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#certifying_auditee_contact_fullname').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          addValidInfo('#certifying_auditee_contact_fullname');
          cy.get('#certifying_auditee_contact_fullname-not-null').should(
            'not.be.visible'
          );
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidInfo('#certifying_auditee_contact_fullname');
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });
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
          addValidInfo('#certifying_auditee_contact_email');
          cy.get('#certifying_auditee_contact_email-error-message').should(
            'not.be.visible'
          );
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidInfo('#certifying_auditee_contact_email');
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });

      describe('Email Address Confirmation', () => {
        it('should display an error message when input does not match email field', () => {
          addValidInfo('#certifying_auditee_contact_email');
          cy.get('#certifying_auditee_contact_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#certifying_auditee_contact_re_email-must-match').should(
            'be.visible'
          );
        });

        it('should remove the error message when input matches email field', () => {
          addValidInfo('#certifying_auditee_contact_email');
          addValidInfo('#certifying_auditee_contact_re_email');
          cy.get('#certifying_auditee_contact_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });
    });

    describe('Auditor certifying official', () => {
      
      describe('Full name', () => {
        it('should display an error message when left blank', () => {
          cy.get('#certifying_auditor_contact_fullname').click().blur();
          cy.get('#certifying_auditor_contact_fullname-not-null').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#certifying_auditor_contact_fullname').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          addValidInfo('#certifying_auditor_contact_fullname');
          cy.get('#certifying_auditor_contact_fullname-not-null').should(
            'not.be.visible'
          );
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidInfo('#certifying_auditor_contact_fullname');
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });

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
          addValidInfo('#certifying_auditor_contact_email')
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
          addValidInfo('#certifying_auditor_contact_email')
          cy.get('#certifying_auditor_contact_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#certifying_auditor_contact_re_email-must-match').should(
            'be.visible'
          );
        });

        it('should remove the error message when input matches email field', () => {
          addValidInfo('#certifying_auditor_contact_email')
          addValidInfo('#certifying_auditor_contact_re_email')

          cy.get('#certifying_auditor_contact_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });
    });

    describe('Auditee contacts', () => {
      
      describe('Full name', () => {
        it('should display an error message when left blank', () => {
          cy.get('#auditee_contacts_fullname').click().blur();
          cy.get('#auditee_contacts_fullname-not-null').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#auditee_contacts_fullname').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          addValidInfo('#auditee_contacts_fullname')
          cy.get('#auditee_contacts_fullname-not-null').should(
            'not.be.visible'
          );
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidInfo('#auditee_contacts_fullname');
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });

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
          addValidInfo('#auditee_contacts_email')
          cy.get('#auditee_contacts_email-email').should('not.be.visible');
        });
      });

      describe('Email Address Confirmation', () => {
        it('should display an error message when input does not match email field', () => {
          addValidInfo('#auditee_contacts_email')

          cy.get('#auditee_contacts_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#auditee_contacts_re_email-must-match').should('be.visible');
        });

        it('should remove the error message when input matches email field', () => {
          addValidInfo('#auditee_contacts_email')
          addValidInfo('#auditee_contacts_re_email')

          cy.get('#auditee_contacts_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });

      it('should allow adding new contact fields', () => {
        cy.get('.auditee_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 4);
        });
      });

      it('should allow deleting additional contact fields', () => {
        cy.get('.auditee_contacts').within(() => {
          cy.get('button').click();
        });

        cy.get('.auditee_contacts .delete-contact').click();
        cy.get('.auditee_contacts .grid-row').should('have.length', 3);
      });

      it('should be able to add contact and contact info to new inputs', () => {
        cy.get('.auditee_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 4);
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
      
      describe('Full name', () => {
        it('should display an error message when left blank', () => {
          cy.get('#auditor_contacts_fullname').click().blur();
          cy.get('#auditor_contacts_fullname-not-null').should(
            'be.visible'
          );
        });

        it('should disable the submit button when fields are left blank', () => {
          cy.get('#auditor_contacts_fullname').click().blur();
          cy.get('button').contains('Create').should('be.disabled');
        });

        it('should remove the error message when input is supplied', () => {
          addValidInfo('#auditor_contacts_fullname');
          cy.get('#auditor_contacts_fullname-not-null').should(
            'not.be.visible'
          );
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidInfo('#auditor_contacts_fullname');
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });
      
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
          addValidInfo('#auditor_contacts_email')
          cy.get('#auditor_contacts_email-email').should('not.be.visible');
        });

        it('should enable the "Create" button when entities are fixed', () => {
          addValidInfo('#auditor_contacts_email')
          cy.get('button').contains('Create').should('not.be.disabled');
        });
      });

      describe('Email Address Confirmation', () => {
        it('should display an error message when input does not match email field', () => {
          addValidInfo('#auditor_contacts_email')

          cy.get('#auditor_contacts_re_email')
            .clear()
            .type('test.address-wit')
            .blur();
          cy.get('#auditor_contacts_re_email-must-match').should('be.visible');
        });

        it('should remove the error message when input matches email field', () => {
          addValidInfo('#auditor_contacts_email')
          addValidInfo('#auditor_contacts_re_email')

          cy.get('#auditor_contacts_re_email-must-match').should(
            'not.be.visible'
          );
        });
      });

      it('should allow adding new contact fields', () => {
        cy.get('.auditor_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 4);
        });
      });

      it('should allow deleting additional contact fields', () => {
        cy.get('.auditor_contacts').within(() => {
          cy.get('button').click();
        });

        cy.get('.auditor_contacts .delete-contact').click();
        cy.get('.auditor_contacts .grid-row').should('have.length', 3);
      });

      it('should be able to add contact and contact info to new inputs', () => {
        cy.get('.auditor_contacts').within(() => {
          cy.get('button').click();
          cy.get('.grid-row').should('have.length', 4);
          cy.get('input[id*="auditor_contacts_fullname"]')
            .eq(1)
            .clear()
            .type('A Name');
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

    it('should proceed to the next step after successful submission', () => {
      testValidAccess();
    });
  });

  it('Canceling an audit submission returns to the home page', () => {
    cy.get('.usa-button').contains('Cancel').click();
    cy.get('.usa-button').contains('OK').click();
    cy.url().should('include', '/audit/');
  });
});
