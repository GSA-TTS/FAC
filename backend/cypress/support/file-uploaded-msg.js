// Displays message if file has already been uploaded
export function testFileUploadMsg(fileSectionName) {
  cy.get('.usa-link').contains(fileSectionName).click();
  cy.get('#already-submitted')
    .invoke('text')
    .then((text) => {
      const expectedText = 'A file has already been uploaded for this section. A successful reupload will overwrite your previous submission.';
      expect(text.trim()).to.equal(expectedText);
    });
};
