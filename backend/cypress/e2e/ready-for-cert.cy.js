
describe('Ready for SF-SAC Certification', () => {
    //replace with your own report ID
    const reportTestId = '2023MAY0001000001'
  
    before(() => {
      cy.visit(`/audit/submission-progress/${reportTestId}`);
    });
    
    it('Page loads successfully', () => {
      cy.url().should('include', `/audit/submission-progress/${reportTestId}`);
    });

    it('clicks Ready for SF-SAC Certification button', () => {
        cy.visit(`/audit/submission-progress/${reportTestId}`);
        cy.get('[href="/audit/ready-for-certification/2023MAY0001000001"] > .usa-button').click();
        cy.url().should('include', `/audit/ready-for-certification/${reportTestId}`);
      });

      it('clicks Submit for Certification', () => {
        cy.visit(`/audit/ready-for-certification/${reportTestId}`);
        cy.get('#continue').click();
      })

});