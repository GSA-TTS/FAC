export function testLogoutGov() {
  cy.get('.usa-menu-btn').contains('Menu').click();
  cy.get('button').contains('Sign out').click();
  
  cy.origin('https://idp.int.identitysandbox.gov/', () => {
    cy.contains('Yes, sign out of Login.gov').click();
  });
  
  // Explicitly return to localhost context after IdP logout redirect
  cy.origin('http://localhost:8000', () => {
    cy.url().should('include', 'localhost:8000');
  });
}
