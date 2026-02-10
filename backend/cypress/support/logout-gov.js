export function testLogoutGov() {
  // Local app sign out (menu -> Sign out)
  cy.get('.usa-menu-btn').contains('Menu').click();
  cy.contains('button', 'Sign out').click();

  // After clicking Sign out, we *might* be redirected to Login.gov for confirmation,
  // or we might stay on localhost depending on environment/session state.
  cy.location('href', { timeout: 30000 }).then((href) => {
    const onLoginGov = href.includes('idp.int.identitysandbox.gov');

    if (!onLoginGov) {
      // Already back on the app (or never left). Nothing else to do.
      return;
    }

    cy.origin('https://idp.int.identitysandbox.gov', () => {
      cy.contains('button, a', 'Yes, sign out of Login.gov', { timeout: 30000 })
        .click({ force: true });
    });
  });

  // Assert we end up back on our app
  cy.location('href', { timeout: 30000 }).should('include', 'localhost');
}