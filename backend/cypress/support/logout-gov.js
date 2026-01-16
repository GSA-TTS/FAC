export function testLogoutGov() {
  cy.origin('http://localhost:8000', () => {
    cy.get('.usa-menu-btn').contains('Menu').click();
    cy.get('button').contains('Sign out').click();
  });
  
  cy.origin('https://idp.int.identitysandbox.gov/', () => {
    cy.contains('Yes, sign out of Login.gov').click();
  });
  
  cy.origin('http://localhost:8000', () => {
    cy.url().should('include', 'localhost:8000');
  });
}