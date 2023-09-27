
export function testTribalAuditForm(optIn, optOut = true){
    const radioButtonId = optIn
    ? 'is_tribal_information_authorized_to_be_public-yes'
    : 'is_tribal_information_authorized_to_be_public-no';
    if(optOut && !optIn){
        cy.get('#is_tribal_information_authorized_to_be_public-yes').click({force:true});
    }
    cy.get(`input#${radioButtonId}`).click({force:true});
    cy.get('#tribal_authorization_certifying_official_name').type('John Wick');
    cy.get('#tribal_authorization_certifying_official_title').type('Offical');
    cy.get('#continue').click();
    cy.url().should('match', /\/audit\/submission-progress\/[0-9A-Z]{17}$/);
}