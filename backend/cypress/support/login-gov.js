const LOGIN_TEST_EMAIL = Cypress.env('LOGIN_TEST_EMAIL');
const LOGIN_TEST_PASSWORD = Cypress.env('LOGIN_TEST_PASSWORD');
const LOGIN_TEST_OTP_SECRET = Cypress.env('LOGIN_TEST_OTP_SECRET');

const IDP_ORIGIN = 'https://idp.int.identitysandbox.gov';

export function testLoginGovLogin(
  email = LOGIN_TEST_EMAIL,
  password = LOGIN_TEST_PASSWORD,
  secret = LOGIN_TEST_OTP_SECRET
) {
  cy.get('a.usa-link[href="/openid/login/"][role="button"]').click();

  cy.get('button.usa-button.sign-in-button')
    .should('contain.text', 'Authenticate with Login.gov')
    .click();

  // Wait until we are EITHER on the IdP or already back on /audit/
  cy.url({ timeout: 30000 }).should((url) => {
    const parsed = new URL(url);
    const onIdp = parsed.origin === IDP_ORIGIN;
    const onAudit = /\/audit\/$/.test(parsed.pathname);
    expect(onIdp || onAudit).to.eq(true);
  });

  // Only do cy.origin() if we actually navigated to the IdP
  cy.url().then((url) => {
    const parsed = new URL(url);
    if (parsed.origin !== IDP_ORIGIN) {
      return; // already authenticated and back on localhost
    }

    cy.origin(
      IDP_ORIGIN,
      { args: { email, password, secret } },
      ({ email, password, secret }) => {
        // email
        cy.get('#user_email');
        cy.get('#user_email').clear();
        cy.get('#user_email').type(email);

        // password
        cy.get('input[id^="password-toggle-input-"]');
        cy.get('input[id^="password-toggle-input-"]').clear();
        cy.get('input[id^="password-toggle-input-"]').type(password, { log: false });

        cy.get('lg-submit-button > .usa-button').click();

        cy.location('pathname', { timeout: 30000 }).should('include', '/login/two_factor');

        cy.task('generateOTP', secret).then((token) => {
          cy.get('input.one-time-code-input__input');
          cy.get('input.one-time-code-input__input').clear();
          cy.get('input.one-time-code-input__input').type(token, { log: false });
        });

        cy.get('lg-submit-button > .usa-button').click();

        // Handle optional interstitials if they appear
        cy.location('pathname', { timeout: 30000 }).then((pathname) => {
          if (pathname.includes('/login/piv_cac_recommended')) {
            cy.get('body').then(($body) => {
              const $skip = $body.find('button.usa-button.usa-button--unstyled[type="submit"]');
              if ($skip.length && $skip.text().includes('Skip')) cy.wrap($skip).click();
            });
          }

          if (pathname.includes('/sign_up/completed')) {
            cy.get('body').then(($body) => {
              const buttons = $body.find('button');
              const match = [...buttons].find((b) =>
                b.innerText?.includes('Agree and continue')
              );
              if (match) cy.wrap(match).click();
            });
          }
        });
      }
    );
  });

  // No matter what happened above, don't return until we are back on localhost /audit/
  cy.location('origin', { timeout: 30000 }).should('include', 'http://localhost:8000');
  cy.location('pathname', { timeout: 30000 }).should('match', /\/audit\/$/);
}