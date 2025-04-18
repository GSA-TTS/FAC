// pass username & password from environment to here to prevent manual entry
const LOGIN_TEST_EMAIL = Cypress.env('LOGIN_TEST_EMAIL');
const LOGIN_TEST_PASSWORD = Cypress.env('LOGIN_TEST_PASSWORD');
const LOGIN_TEST_OTP_SECRET = Cypress.env('LOGIN_TEST_OTP_SECRET');

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

  // We can't wrap all of this in a cy.origin because it will error if it made
  // it back to localhost already, which is the typical case
  cy.url().then((url) => {
    if (url.match(/\/login\/piv_cac_recommended$/)) {
      // Handle the case where the page redirects to piv_cac_recommended
      cy.origin('https://idp.int.identitysandbox.gov/', () => {
        cy.get('button.usa-button.usa-button--unstyled[type="submit"]:contains("Skip")').click();
      });
    } else if (url.match(/\/sign_up\/completed$/)) {
      // Login's additional data sharing consent
      cy.origin('https://idp.int.identitysandbox.gov/', () => {
        cy.get('button:contains("Agree and continue")').click();
      });
    }
  });

  cy.url().should('match', /\/audit\/$/);
};
