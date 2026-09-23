export function testLogoutGov() {
  cy.get('.usa-menu-btn').contains('Menu').click();
  cy.get('nav.usa-nav button').contains('Sign out').click({ force: true });
  cy.origin(
    'https://idp.int.identitysandbox.gov/',
    {},
    () => {
      cy.contains('Yes, sign out of Login.gov').click();
    }
  );
};
