describe('Create New Audit', () => {
  before(() => {
    cy.visit('/audit/new/step-3');
  });

  describe('Fill out form', () => {
    it('does not show any errors initially', () => {
      cy.get('[class*=--error]').should('have.length', 0);
    });

    describe('Auditee certifying official', () => {
      it('fill in Auditee contact fields', () => {
        cy.get('#auditee_certifying_official_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
        cy.get('#auditee_certifying_official_re_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
      });
    });

    describe('Auditor certifying official', () => {
      it('fill in Auditor contact fields', () => {
        cy.get('#auditor_certifying_official_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
        cy.get('#auditor_certifying_official_re_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
      });
    });

    describe('Auditee contacts', () => {
      it('fill in inital contact fields', () => {
        cy.get('#auditee_contacts_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
        cy.get('#auditee_contacts_re_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
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
    describe('auditor contacts', () => {
      it('fill in inital contact fields', () => {
        cy.get('#auditor_contacts_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
        cy.get('#auditor_contacts_re_email')
          .clear()
          .type('test.address-with+features@test.gsa.gov')
          .blur();
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
  });

  describe('Test form submission', () => {
    it('should return ERRORS from the remote server', () => {
      cy.intercept('POST', '/sac/accessandsubmission', {
        errors: true,
      }).as('invalidResponse');

      cy.get('.usa-button').contains('Create').click();

      cy.wait('@invalidResponse').then((interception) => {
        expect(interception.response.body.errors).to.exist;
        console.log('Response:' + interception.response.body.errors);
      });
    });

    it('should return SUCCESS response and move to the next page', () => {
      const reportId = '2022UBT0001000020';
      cy.intercept('POST', '/sac/accessandsubmission', {
        report_id: reportId,
        next: 'TBD',
      }).as('validResponse');

      cy.get('.usa-button').contains('Create').click();

      cy.wait('@validResponse').then((interception) => {
        expect(interception.response.body.report_id).to.exist;
      });
      cy.url().should('include', 'submission');
      cy.url().should('include', `reportId=${reportId}`);
    });
  });
});
