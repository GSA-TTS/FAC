//Currently experimenting login session 

import '../support/commands.js'

describe("Cypress origin API", () => {
    beforeEach(() => {
        cy.login(Cypress.env("EMAIL"), Cypress.env("PASSWORD"));
    });

    it("Page loads correct profile", () => {
        cy.visit('/audit');
        cy.get('form.sign-out span').contains('edward.zapata@gsa.gov').should('exist');
    });

    it('the external, api page only allows authenticated users', () => {
        cy.visit('https://idp.int.identitysandbox.gov/');
    })
})

// it("Authenticates with Login.gov", () => {
//     cy.visit('/')
//     cy.get('a.usa-button.sign-in-button').click();
//     cy.get('button.usa-button.sign-in-button')
//         .should('contain.text', 'Authenticate with Login.gov').click();

//     cy.origin('https://idp.int.identitysandbox.gov/', () => {
//         cy.get('#user_email').type(username);
//         cy.get('input[id^="password-toggle-input-"]').type(password);
//         cy.get('lg-submit-button > .usa-button').click();
//         cy.url().should('contain', 'https://idp.int.identitysandbox.gov/login/two_factor/authenticator');
//     })
// })