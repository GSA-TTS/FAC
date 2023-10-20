export function testFileUploadMsg(fileSectionName) {
  cy.visit(`/audit/`);
  cy.url().should('match', /\/audit\//);
  cy.get(':nth-child(4) > .usa-table > tbody > tr').last().find('td:nth-child(1)>.usa-link').click();
  cy.get('.usa-link').contains(fileSectionName).click();
  cy.get('#already-submitted')
    .invoke('text')
    .then((text) => {
      const expectedText = 'A file has already been uploaded for this section. A successful reupload will overwrite your previous submission.';
      expect(text.trim()).to.equal(expectedText);
    });
}
