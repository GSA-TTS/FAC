import { testCrossValidation } from "./cross-validation";

// test unlock certification
export function testUnlock() {
    cy.url().then(url => {
        const reportId = url.split('/').pop();
        cy.get('.usa-button').contains('Unlock').click();
        cy.get('#continue').contains('Unlock submission').click();
        cy.get('#basic-logo').should('exist').click();
        cy.url().should('match', /\/audit\//);
        cy.contains('td', `${reportId}`)
            .siblings()
            .contains('td', 'In Progress')
            .click()
        cy.url().should('match', /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
        cy.then(() => {
            cy.get(".usa-link").contains("Pre-submission validation").click();
            testCrossValidation();
        });
    });
}