// pass username & password from environment to here to prevent manual entry
const LOGIN_TEST_EMAIL = Cypress.env('LOGIN_TEST_EMAIL');
const LOGIN_TEST_PASSWORD = Cypress.env('LOGIN_TEST_PASSWORD');
const LOGIN_TEST_OTP_SECRET = Cypress.env('LOGIN_TEST_OTP_SECRET');

function handleLoginGovInterstitialIfPresent() {
  cy.location('href').then((href) => {
    if (href.includes('localhost') || href.match(/\/audit\/$/)) return;

    if (href.match(/\/login\/piv_cac_recommended$/)) {
      cy.origin('https://idp.int.identitysandbox.gov/', () => {
        cy.contains('button', /^Skip$/).click();
      });
      return;
    }

    if (href.match(/\/sign_up\/completed$/)) {
      cy.origin('https://idp.int.identitysandbox.gov/', () => {
        cy.contains('button', 'Agree and continue').click();
      });
    }
  });
}

export function testLoginGovLogin(
  email = LOGIN_TEST_EMAIL, password = LOGIN_TEST_PASSWORD, secret = LOGIN_TEST_OTP_SECRET) {
  cy.get('a.usa-link[href="/openid/login/"][role="button"]').click();
  cy.get('button.usa-button.sign-in-button')
    .should('contain.text', 'Authenticate with Login.gov')
    .click();

  cy.origin(
    'https://idp.int.identitysandbox.gov/',
    {
      args: { email, password, secret },
    },
    ({ email, password, secret }) => {
      cy.get('#user_email').type(email);
      cy.get('input[id^="password-toggle-input-"]').type(password);
      cy.get('lg-submit-button > .usa-button').click();
      cy.url().should(
        'contain',
        'https://idp.int.identitysandbox.gov/login/two_factor/authenticator'
      );
      cy.task('generateOTP', secret).then((token) => {
        cy.get('input.one-time-code-input__input').type(token);
      });
      cy.get('lg-submit-button > .usa-button').click();
    });

 // Wait until either we’re back on localhost OR we’re on a known Login.gov interstitial.
  cy.location('href', { timeout: 20000 }).should((href) => {
    expect(
      href.includes('localhost') ||
        href.includes('/login/piv_cac_recommended') ||
        href.includes('/sign_up/completed')
    ).to.eq(true);
  });

  // Handle at most 2 interstitials (sometimes you get one after another)
  handleLoginGovInterstitialIfPresent();

  cy.location('href', { timeout: 20000 }).then((href) => {
    if (
      href.includes('/login/piv_cac_recommended') ||
      href.includes('/sign_up/completed')
    ) {
      handleLoginGovInterstitialIfPresent();
    }
  });

  cy.url({ timeout: 20000 }).should('match', /\/audit\/$/);
};
