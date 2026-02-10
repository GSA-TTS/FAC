// pass username & password from environment to here to prevent manual entry
const LOGIN_TEST_EMAIL = Cypress.env('LOGIN_TEST_EMAIL');
const LOGIN_TEST_PASSWORD = Cypress.env('LOGIN_TEST_PASSWORD');
const LOGIN_TEST_OTP_SECRET = Cypress.env('LOGIN_TEST_OTP_SECRET');

function handleLoginGovInterstitialIfPresent() {
  cy.location('pathname', { timeout: 30000 }).then((pathname) => {
    if (pathname.match(/\/login\/piv_cac_recommended$/)) {
      cy.origin('https://idp.int.identitysandbox.gov/', () => {
        cy.contains('button', 'Skip', { timeout: 30000 }).click();
      });
      return;
    }

    if (pathname.match(/\/sign_up\/completed$/)) {
      cy.origin('https://idp.int.identitysandbox.gov/', () => {
        cy.contains('button', 'Agree and continue', { timeout: 30000 }).click();
      });
    }
  });
}

export function testLoginGovLogin(
  email = LOGIN_TEST_EMAIL,
  password = LOGIN_TEST_PASSWORD,
  secret = LOGIN_TEST_OTP_SECRET
) {
  cy.get('a.usa-link[href="/openid/login/"][role="button"]').click();
  cy.get('button.usa-button.sign-in-button')
    .should('contain.text', 'Authenticate with Login.gov')
    .click();

  cy.origin(
    'https://idp.int.identitysandbox.gov/',
    { args: { email, password, secret } },
    ({ email, password, secret }) => {
      cy.get('#user_email').type(email);
      cy.get('input[id^="password-toggle-input-"]').type(password);
      cy.get('lg-submit-button > .usa-button').click();

      // Safer than asserting full URL
      cy.location('pathname').should('contain', '/login/two_factor/authenticator');

      cy.task('generateOTP', secret).then((token) => {
        cy.get('input.one-time-code-input__input').type(token);
      });

      cy.get('lg-submit-button > .usa-button').click();
    }
  );

  // After OTP submit, Login.gov may show an interstitial OR redirect straight back to localhost.
  cy.location('href', { timeout: 30000 }).then((href) => {
    if (!href.includes('identitysandbox.gov')) return;
    handleLoginGovInterstitialIfPresent();
  });

  // Re-check interstitials again in case the first redirect lands on one.
  handleLoginGovInterstitialIfPresent();

  // Final: ensure we're back on our app
  cy.location('href', { timeout: 30000 }).should('not.include', 'identitysandbox.gov');
  cy.location('pathname', { timeout: 30000 }).should('match', /\/audit\/$/);
}