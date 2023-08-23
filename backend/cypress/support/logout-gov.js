
export function testLogoutGov() {
  cy.get('button').contains('Menu').click();
  cy.get('button').contains('Sign out').click();
  // cy.url().should('match', /\/opendid\/logout\/$/);
  cy.origin(
    'https://idp.int.identitysandbox.gov/',
    {},
    () => {
      cy.contains('Yes, sign out of Login.gov').click();
    }
  );
}