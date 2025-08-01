describe('Resubmit an Audit', () => {
  beforeEach(() => {
    cy.session('loginSession', () => {
      cy.visit('/')
      cy.login();
    });

    cy.visit('/audit/resubmission-start');
  });

  it('Cancel', () => {
    cy.get('[id=cancel]').click();
    cy.url().should('include', '/audit');
  });

  it('Blank report ID', () => {
    cy.get('[id=continue]').click();
    cy.url().should('include', '/resubmission-start');
    cy.get('[id=error]').contains('This field is required.');
  });

  it('Short report ID', () => {
    cy.get('[id=report_id]').type('TOO-SHORT');
    cy.get('[id=continue]').click();
    cy.url().should('include', '/resubmission-start');
    cy.get('[id=error]').contains('The given report ID is too short!');
  });

  it('Long report ID', () => {
    cy.get('[id=report_id]').type('WAYYYYY-TOOOOOOO-LONGGGGGGGGGG');
    cy.get('[id=continue]').click();
    cy.url().should('include', '/resubmission-start');
    cy.get('[id=error]').contains('The given report ID is too long!');
  });

  it('Report ID not found', () => {
    cy.get('[id=report_id]').type('YYYY-MM-SOURCE-0123456789');
    cy.get('[id=continue]').click();
    cy.url().should('include', '/resubmission-start');
    cy.get('[id=error]').contains('Audit to resubmit not found.');
  });

  it('Valid report ID', () => {
    // This assumes full-submission has been run after a make-clean. You can
    // instead replace this with any other valid report ID you have locally.
    cy.get('[id=report_id]').type('2023-12-GSAFAC-0000000003');
    cy.get('[id=continue]').click();
    cy.url().should('include', '/report_submission/eligibility/');
  });
});
