class searchPage {
    //encapsulate page elements within a elements object
    elements = {
        yearCheckboxById: (year) => cy.get((year.toLowerCase() === 'all_years' ? '#audit-year [id^="audit-year-"]' : `#audit-year-${year}`)),
        entityNameAccordionBtn: () => cy.get('.usa-accordion__button:contains("Name (Entity, Auditee, or Auditor)")'),
        ueiOrEinField: () => cy.get('#uei-or-ein'),
        alnField: () => cy.get('#aln'),
        entityNameField: () => cy.get('#entity-name'),
        startDateField: () => cy.get('#start-date'),
        stateAccordionBtn: () => cy.get('.usa-accordion__button:contains("State")'),
        cogOrOverAccordionBtn: () => cy.get('.usa-accordion__button:contains("Cognizant or Oversight")'),
        alnAccordionBtn: () => cy.get('.usa-accordion__button:contains("Assistance Listing Number (formerly CFDA")'),
        endDateField: () => cy.get('#end-date'),
        auditeeState: () => cy.get('#auditee_state'),
        optionsField: () => cy.get('#options'),
        auditFindingsAccordionBtn: () => cy.get('.usa-accordion__button:contains("Audit findings")'),
        findingsCheckboxId: (findings) => cy.get(`.usa-checkbox__input[value="${findings.toLowerCase()}"]`),
        directFundingAccordionBtn: () => cy.get('.usa-accordion__button:contains("Direct funding")'),
        directFundingCheckbox: () => cy.get('#usa-checkbox__input[value="${value}"]'),
        directFundingCheckboxId: (funding) => cy.get(`.usa-checkbox__input[value="${funding.toLowerCase()}"]`),
        facAcceptDateAccordionBtn: () => cy.get('.usa-accordion__button:contains("FAC acceptance date")'),
        majorProgramAccordionBtn: () => cy.get('.usa-accordion__button:contains("Major program")'),
        majorProgramRadio: () => cy.get('.usa-radio__input[name="major_program"]'),
        searchSubmitBtn: () => cy.get('input.usa-button[type="submit"][value="Search"]'),
        searchTable: () => cy.get('.usa-table'),
        advanceSearchBtn: () => cy.get('a[href="/dissemination/search/advanced/"]'),
        sfSacDownloadBtn: () => cy.get('a.usa-button p:contains("SF-SAC")'),
        singleAuditBtn: () => cy.get('a.usa-button p:contains("Single audit report")'),
        fiscalYearEndMonthBtn: () => cy.get('.usa-accordion__button:contains("Fiscal year end month")'),
        typeRequirementAccordionBtn: () => cy.get('.usa-accordion__button:contains("Type Requirement")'),
        typeRequirementField: () => cy.get('#type-requirement-input'),
        entityTypeAccordionBtn: () => cy.get('.usa-accordion__button:contains("Entity type")'),
        passThroughNameAccordionBtn: () => cy.get('.usa-accordion__button:contains("Passthrough Name")'),
        passThroughNameField: () => cy.get('#passthrough-name'),
        reportId: () => cy.get('.usa-accordion__button:contains("Report ID")'),
        fyEndMonth: () => cy.get('#fy_end_month'),
        entityTypeCheckboxId: (entity) => cy.get(`.usa-checkbox__input[value="${entity}"]`),
        reportdIdAccordionBtn: () => cy.get('.usa-accordion__button:contains("Report ID")'),
        reportIdField: () => cy.get('#report-id')
    };

    clickSearchSubmitButton() {
        this.elements.searchSubmitBtn().last().click();
    };

    downloadSfSac(url) {
        const reportId = url.split('/').pop();
        const downloadUrl = Cypress.config().baseUrl + `/dissemination/summary/${reportId}`
        this.elements.sfSacDownloadBtn().should('exist').click();
        cy.downloadFile(downloadUrl, 'cypress/downloads', '2022-12-GSAFAC-0000000001.xlsx');
    }

    downloadSumReport(url) {
        const reportId = url.split('/').pop();
        const downloadUrl = Cypress.config().baseUrl + `/dissemination/summary/${reportId}`
        this.elements.singleAuditBtn().click();
        cy.downloadFile(downloadUrl,
            'cypress/downloads', '2022-12-GSAFAC-0000000001.pdf');
    };
};

//assertions should be in tests not in POM
//     checkAuditYearCheckbox(year) {
//         cy.get(this.yearCheckboxById(year)).should('be.checked').and('have.value', year);
//     };

//     uncheckAuditYearCheckbox(year) {
//         cy.get(this.yearCheckboxById(year)).uncheck({ force: true }).should('not.be.checked').and('have.value', year);
//     };

//     checkAllYearsCheckbox(year) {
//         cy.get(this.yearCheckboxById('all_years')).check({ force: true }).should('be.checked').and('have.value', year);
//     };

// testUEIorEin(value) {
//     // cy.get(this.accordionButton).contains('UEI or EIN').as('accordionButton').click();
//     cy.get(this.ueiOrEinField).clear().type(value);
// };

//     testALN(value) {
//         cy.get(this.accordionBtn).contains('Assistance Listing Number (formerly CFDA').as('accordionButton').click();
//         cy.get(this.alnField).clear().type(value);
//     };

// testName(value) {
//     cy.get(this.accordionBtn).contains('Name (Entity, Auditee, or Auditor)').as('accordionButton').click();
//     cy.get(this.entityNameField).clear().type(value);
// };

// testFACacceptanceDate(startDate, endDate) {
//     cy.get(this.accordionBtn).contains('FAC acceptance date').as('accordionButton').click();
//     cy.get(this.startDateField).clear().type(startDate);
//     cy.get(this.endDateField).clear().type(endDate);
// };

// testState(value) {
//     cy.get(this.accordionBtn).contains('State').as('accordionButton').click();
//     cy.get(this.auditeeState).select(value);
// };

//     testCogorOver(value) {
//         cy.get(this.accordionBtn).contains('Cognizant or Oversight').as('accordionButton').click();
//         cy.get(this.optionsField).select(value);
//     };

//     openFindingsAccordion() {
//         cy.get(this.findingsAccordionBtn).as('accordionButton').click();
//     };

//     checkAuditFindingsCheckbox(findings) {
//         cy.get(this.findingsCheckboxId(findings)).check({ force: true }).should('be.checked').and('have.value', findings);
//     };

//     uncheckAuditFindingsCheckbox(findings) {
//         cy.get(this.findingsCheckboxId(findings)).uncheck({ force: true }).should('not.be.checked').and('have.value', findings);
//     };

//     openDirectFundingAccordion() {
//         cy.get(this.directFundingAccordionBtn).as('accordionButton').click();
//     };

//     checkDirectFundingCheckbox(funding) {
//         cy.get(this.directFundingCheckboxId(funding)).check({ force: true }).should('be.checked').and('have.value', funding);
//     };

//     uncheckDirectFundingCheckbox(funding) {
//         cy.get(this.directFundingCheckboxId(funding)).uncheck({ force: true }).should('not.be.checked').and('have.value', funding);
//     };

//     openMajorProgramAccordion() {
//         cy.get(this.majorProgramAccordionBtn).as('accordionButton').click();
//     };

//     checkMajorProgramRadio(value) {
//         cy.get(`${this.majorProgramRadio}[value="${value}"]`).check({ force: true }).should('be.checked').and('have.value', value);
//     };

//     uncheckMajorProgramRadio(value) {
//         cy.get(`${this.majorProgramRadio}[value="${value}"]`).check({ force: true }).should('be.checked').and('have.value', value);
//     };

// openAndSelectFyEndMonth(value) {
//     cy.get(this.fiscalYearEndMonthBtn).as('accordionButton').click();
//     cy.get(this.fyEndMonth).select(value);
// };

//     openAndSelectEntityTypeCheckbox(entity) {
//         cy.get(this.entityTypeBtn).as('accordionButton').click();
//         cy.get(this.entityTypeCheckboxId(entity)).check({ force: true }).should('be.checked').and('have.value', entity);
//     };

//     testReportId(value) {
//         cy.get(this.reportdIdAccordionBtn).as('accordionButton').click();
//         cy.get(this.reportIdField).clear().type(value);
//     };

//     testTypeRequirement(value) {
//         cy.get(this.typeRequirementBtn).as('accordionButton').click();
//         cy.get(this.typeRequirementField).clear().type(value);
//     };

//     testSearchSubmitButton() {
//         cy.get(`${this.searchSubmitBtn}:last`).click();
//     };

// testSearchTable() {
//     cy.get(this.searchTable).should('exist');
//     cy.contains('td', 'D7A4J33FUMJ1')
//         .siblings()
//         .find('a.usa-link[href^="/dissemination/summary"]')
//         .should('have.attr', 'target', '_blank')
//         .invoke('removeAttr', 'target')
//         .click()

//     cy.url().should('include', '/dissemination/summary');
// };

//     testAdvSearch() {
//         cy.get(this.advanceSearchBtn).should('contain', 'advanced search').click();
//     };

//     testSummaryReport() {
//         cy.url().then(url => {
//             const reportId = url.split('/').pop();
//             cy.url().should('include', `/dissemination/summary/${reportId}`);
//             cy.get(this.sfSacDownloadBtn).should('exist').click();
//             //single audit report pdf may not appear for certain audits
//             //cy.get(this.singleAuditBtn).should('exist').click();
//             cy.wait(5000);
//             this.testSfSacDownload(url);
//             //this.testSumReportDownload(url);
//         });
//     };

//     testSfSacDownload(url) {
//         const reportId = url.split('/').pop();
//         const downloadUrl = Cypress.config().baseUrl + `/dissemination/summary/${reportId}`
//         cy.downloadFile(downloadUrl,
//             'cypress/downloads', '2022-12-GSAFAC-0000000001.xlsx');
//     };
//     testSumReportDownload(url) {
//         const reportId = url.split('/').pop();
//         const downloadUrl = Cypress.config().baseUrl + `/dissemination/summary/${reportId}`
//         cy.downloadFile(downloadUrl,
//             'cypress/downloads', '2022-12-GSAFAC-0000000001.pdf');
//     };
// };

export default searchPage;