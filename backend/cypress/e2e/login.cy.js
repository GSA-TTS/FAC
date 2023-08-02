describe('login', () => {
  // pass username & password from environment to here to prevent manual entry
  const LOGIN_TEST_EMAIL = Cypress.env('LOGIN_TEST_EMAIL');
  const LOGIN_TEST_PASSWORD = Cypress.env('LOGIN_TEST_PASSWORD');
  const LOGIN_TEST_OTP_SECRET = Cypress.env('LOGIN_TEST_OTP_SECRET');

  // To set DISABLE_AUTH in Cypress, set the environment variable
  // CYPRESS_DISABLE_AUTH in the OS. If it's not set, default to false
  const disableAuth = Cypress.env('DISABLE_AUTH') || false; 

  before(() => {
    // run the task once and it memorizes the secret
    cy.task("generateOTP", LOGIN_TEST_OTP_SECRET);
  });

  beforeEach(() => {
       cy.visit('/');
   });

   it('Page loads successfully', () => {
       cy.url().should('include', '/');
   });

  //This uses a IF/ Else statement whether authentication is required based if DISABLE_AUTH is True/False
  describe('authenticate with Login.gov', () => {
      if (!disableAuth) {
          it('should login with email, password and OTP', () => {
              cy.get('a.usa-button.sign-in-button').click();
              cy.get('button.usa-button.sign-in-button')
                  .should('contain.text', 'Authenticate with Login.gov').click();
              cy.origin('https://idp.int.identitysandbox.gov/',
                        {args: {LOGIN_TEST_EMAIL, LOGIN_TEST_PASSWORD}},
                        ({LOGIN_TEST_EMAIL, LOGIN_TEST_PASSWORD}) => {
                  cy.get('#user_email').type(LOGIN_TEST_EMAIL);
                  cy.get('input[id^="password-toggle-input-"]').type(LOGIN_TEST_PASSWORD);
                  cy.get('lg-submit-button > .usa-button').click();
                  cy.url().should('contain', 'https://idp.int.identitysandbox.gov/login/two_factor/authenticator');
                  cy.task("generateOTP").then(token => {
                    cy.get('input.one-time-code-input__input').type(token);
                  });
                  cy.get('lg-submit-button > .usa-button').click();
                  cy.url().then((url) => {
                    if (url.match(/\/sign_up\/completed$/)) {
                      // Login's additional data sharing consent
                      cy.get('button:contains("Agree and continue")').click();
                    }
                  });
              })
              cy.url().should('match', /\/audit\/$/);
            });
          } else {
          it('should not require authentication', () => {
              cy.url().should('match', /\/audit\/$/)
          });
      }
  });

});
