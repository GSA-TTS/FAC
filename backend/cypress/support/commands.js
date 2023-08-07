// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//import '@cypress-audit/lighthouse/commands';
//import '@cypress-audit/pa11y/commands';
import 'cypress-file-upload';

// Cypress.Commands.add('login', (email, password) => {
//     cy.session([email, password], () => {
//         cy.visit('/');
//         cy.get('a.usa-button.sign-in-button').click();

//         cy.origin(
//             'https://idp.int.identitysandbox.gov/',
//             { args: [email, password] },
//             ([email, password]) => {
//                 cy.get('#user_email').type(email);
//                 cy.get('input[id^="password-toggle-input-"]').type(password);
//                 cy.get('lg-submit-button > .usa-button').click();
//             }

//         )
//         cy.url().should('contain', 'https://idp.int.identitysandbox.gov/login/two_factor/authenticator');
//     })
// })

// Cypress.Commands.add('login', () => {
//     const email = 'edward.zapata@gsa.gov';
//     const password = 'Testsitechange1!';
//     cy.visit('/');
//     cy.get('a.usa-button.sign-in-button').click();
//     cy.get('button.usa-button.sign-in-button')
//         .should('contain.text', 'Authenticate with Login.gov').click();
//     cy.origin('https://idp.int.identitysandbox.gov/', () => {
//         cy.get('#user_email').type(email);
//         cy.get('input[id^="password-toggle-input-"]').type(password);
//         cy.get('lg-submit-button > .usa-button').click();
//         cy.url().should('contain', 'https://idp.int.identitysandbox.gov/login/two_factor/authenticator');
//         //cy.get('#code-776936')
//     })
//})

// Cypress.Commands.add('login', (email, password) => {
//     cy.visit('/');
//     cy.get('a.usa-button.sign-in-button').click();

//     cy.origin(
//         'https://idp.int.identitysandbox.gov/',
//         { args: [email, password] },
//         ([email, password]) => {
//             cy.get('#user_email').type(email);
//             cy.get('input[id^="password-toggle-input-"]').type(password);
//             cy.get('lg-submit-button > .usa-button').click();
//         }

//     )
//     cy.url().should('contain', 'https://idp.int.identitysandbox.gov/login/two_factor/authenticator');
// })
//

import { testLoginGovLogin } from './login-gov.js';

Cypress.Commands.add('login', () => {
  testLoginGovLogin();
})
