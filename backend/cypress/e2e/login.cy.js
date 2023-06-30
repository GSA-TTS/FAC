import '../support/commands.js'
//require('dotenv').config();

describe('login', () => {
    //const username = Cypress.env('USERNAME');
    //const password = Cypress.env('PASSWORD');
    // const disableAuth = Cypress.env('DISABLE_AUTH'); //Console says disableAuth is undefined
    // const disableAuth = true -- this works

    beforeEach(() => {
        cy.visit('/');
    });

    it('Page loads successfully', () => {
        cy.url().should('include', '/');
    });

    describe('authenticate with login.gov', () => {
        it('should log in with credentials', () => {
            cy.login();
        })
    })
    // describe('authenticate with Login.gov', () => {
    //     console.log('disableAuth:', disableAuth);
    //     if (!disableAuth) {
    //         it('should navigate to authentication login', () => {
    //             cy.get('a.usa-button.sign-in-button').click();
    //             cy.get('button.usa-button.sign-in-button')
    //                 .should('contain.text', 'Authenticate with Login.gov').click();
    //             cy.origin('https://idp.int.identitysandbox.gov/', () => {
    //                 cy.get('#user_email').type('edward.zapata@gsa.gov');
    //                 cy.get('input[id^="password-toggle-input-"]').type('Testsitechange1!');
    //                 cy.get('lg-submit-button > .usa-button').click();
    //                 cy.url().should('contain', 'https://idp.int.identitysandbox.gov/login/two_factor/authenticator');
    //                 cy.get('#code-776936')
    //             })
    //         });
    //     } else {
    //         it('should not require authentication', () => {
    //             cy.url().should('contain', 'http://localhost:8000/audit/')
    //         });
    //     }
    // });
});



