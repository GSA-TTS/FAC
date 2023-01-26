describe('Create New Audit', () => {
  before(() => {
    cy.visit('/audit/new/step-1');
  });

  describe('Pre-test populate form', () => {
    it('should remove errors when valid properties are checked', () => {
      cy.get('label[for=entity-state]').click();
      cy.get('label[for=spend-yes]').click();
      cy.get('label[for=us-yes]').click();
      cy.get('[class*=--error]').should('have.length', 0);
    });

    it('should hide error messages when invalid entities are fixed', () => {
      cy.get('.usa-error-message:visible').should('have.length', 0);
    });

    it('should enable the "Continue" button when entities are fixed', () => {
      cy.get('button').contains('Continue').should('not.be.disabled');
    });
  });

  describe('Eligibility validation via API', () => {
    it('should return eligibility errors from the remote server', () => {
      cy.intercept('POST', '/sac/eligibility', {
        eligible: false,
        errors: 'Not eligible.',
      }).as('noteligible');

      cy.get('.usa-button').contains('Continue').click();

      cy.wait('@noteligible').then((interception) => {
        assert.isNotNull(interception.response.body, '1st API call has data');
      });
    });

    it('should return success response and move to the next page', () => {
      cy.intercept('POST', '/sac/eligibility', {
        eligible: true,
        next: 'sac/auditee',
      }).as('eligibleResponse');

      cy.get('.usa-button').contains('Continue').click();

      cy.wait('@eligibleResponse').then((interception) => {
        assert.isNotNull(interception.response.body, '1st API call has data');
        cy.url().should('include', '/audit/new/step-2/');
      });
    });
  });
});
