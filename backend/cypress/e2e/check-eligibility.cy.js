describe('Create New Audit', () => {
  before(() => {
    cy.visit('/audit/new/step-1');
  });

  describe('A Blank Form', () => {
    it('marks empty responses as invalid', () => {
      cy.get('fieldset.question:invalid').should('have.length', 3);
    });

    it('will not submit', () => {
      cy.get('.usa-form--large').invoke('submit', (e) => {
        e.preventDefault();
        throw new Error('Form was submitted'); // The test will fail if this error is thrown
      });

      cy.get('.usa-button').contains('Continue').click();
    });

    it('sets focus on the first invalid input', () => {
      cy.get('.usa-button').contains('Continue').click();
      cy.focused().should('have.attr', 'type', 'radio');
    });
  });

  describe('Validation', () => {
    it('does not show any errors initially', () => {
      cy.get('[class*=--error]').should('have.length', 0);
    });

    it('should mark errors when invalid properties are checked', () => {
      // This needs to be a click on the label rather than a
      // check on the input itself because of the CSS magic
      // USWDS does to make the fancy radio buttons
      cy.get('label[for=entity-none]').click();
      cy.get('label[for=spend-no]').click();
      cy.get('label[for=us-no]').click();
      cy.get('[class*=--error]').should('have.length', 3);
    });

    it('should display error messages for invalid entities', () => {
      cy.get('.usa-error-message:visible').should('have.length', 3);
    });

    it('should disable the "Continue" button when an entity is invalid', () => {
      cy.get('button').contains('Continue').should('be.disabled');
    });

    it('should remove errors when valid properties are checked', () => {
      cy.get('label[for=entity-state]').click();
      cy.get('label[for=spend-yes]').click();
      cy.get('label[for=us-yes]').click();
      cy.get('[class*=--error]').should('have.length', 0);
    });

    xit('should hide error messages when invalid entities are fixed', () => {
      cy.get('.usa-error-message:visible').should('have.length', 0);
    });

    it('should enable the "Continue" button when entities are fixed', () => {
      cy.get('button').contains('Continue').should('not.be.disabled');
    });
  });
});
