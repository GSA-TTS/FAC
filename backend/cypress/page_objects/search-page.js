class searchPage {
    constructor() {
        this.auditYearCheckbox = '#audit-year input[type="checkbox"]';
        //define a function 'yearCheckboxById' that takes a 'year' argument. Using a dynamic selector.
        this.yearCheckboxById = (year) => (year.toLowerCase() === 'all_years' ? '#audit-year [id^="audit-year-"]' : `#audit-year-${year}`);
        this.accordionBtn = '.usa-accordion__button';
        this.ueiOrEinField = '#uei-or-ein';
        this.alnField = '#aln';
        this.entityNameField = '#entity-name';
        this.startDateField = '#start-date';
        this.endDateField = '#end-date';
        this.auditeeState = '#auditee_state';
        this.optionsField = '#options';
        this.findingsAccordionBtn = '.usa-accordion__button:contains("Audit findings")';
        this.auditFindingsCheckbox = '#usa-checkbox__input[value="${value}"]';
        this.findingsCheckboxId = (findings) => `.usa-checkbox__input[value="${findings.toLowerCase()}"]`;
        this.directFundingAccordionBtn = '.usa-accordion__button:contains("Direct funding")';
        this.directFundingCheckbox = '#usa-checkbox__input[value="${value}"]';
        this.directFundingCheckboxId = (funding) => `.usa-checkbox__input[value="${funding.toLowerCase()}"]`;
        this.majorProgramAccordionBtn = '.usa-accordion__button:contains("Major program")';
        this.majorProgramRadio = '.usa-radio__input[name="major_program"]';
        this.searchSubmitBtn = 'input.usa-button[type="submit"][value="Search"]';
        this.searchTable = '.usa-table';
        this.advanceSearchBtn = 'a[href="/dissemination/search/advanced/"]';
        //summaryReport
        this.sfSacDownloadBtn = 'a.usa-button p:contains("SF-SAC")';
        this.singleAuditBtn = 'a.usa-button p:contains("Single audit report")';
        this.fiscalYearEndMonthBtn = '.usa-accordion__button:contains("Fiscal year end month")';
        this.typeRequirementBtn = '.usa-accordion__button:contains("Type Requirement")';
        this.typeRequirementField = '#type-requirement-input';
        this.entityTypeBtn = '.usa-accordion__button:contains("Entity type")';
        this.passThroughName = '.usa-accordion__button:contains("Passthrough Name")';
        this.reportId = '.usa-accordion__button:contains("Report ID")';
        this.fyEndMonth = '#fy_end_month';
        this.entityTypeCheckboxId = (entity) => `.usa-checkbox__input[value="${entity}"]`;
        this.reportdIdAccordionBtn = '.usa-accordion__button:contains("Report ID")';
        this.reportIdField = '#report-id';
    };

    checkAuditYearCheckbox(year) {
        cy.get(this.yearCheckboxById(year)).should('be.checked').and('have.value', year);
    };

    uncheckAuditYearCheckbox(year) {
        cy.get(this.yearCheckboxById(year)).uncheck({ force: true }).should('not.be.checked').and('have.value', year);
    };

    checkAllYearsCheckbox(year) {
        cy.get(this.yearCheckboxById('all_years')).check({ force: true }).should('be.checked').and('have.value', year);
    };

    testUEIorEin(value) {
        // cy.get(this.accordionButton).contains('UEI or EIN').as('accordionButton').click();
        cy.get(this.ueiOrEinField).clear().type(value);
    };

    testALN(value) {
        cy.get(this.accordionBtn).contains('Assistance Listing Number (formerly CFDA').as('accordionButton').click();
        cy.get(this.alnField).clear().type(value);
    };

    testName(value) {
        cy.get(this.accordionBtn).contains('Name (Entity, Auditee, or Auditor)').as('accordionButton').click();
        cy.get(this.entityNameField).clear().type(value);
    };

    testFACacceptanceDate(startDate, endDate) {
        cy.get(this.accordionBtn).contains('FAC acceptance date').as('accordionButton').click();
        cy.get(this.startDateField).clear().type(startDate);
        cy.get(this.endDateField).clear().type(endDate);
    };

    testState(value) {
        cy.get(this.accordionBtn).contains('State').as('accordionButton').click();
        cy.get(this.auditeeState).select(value);
    };

    testCogorOver(value) {
        cy.get(this.accordionBtn).contains('Cognizant or Oversight').as('accordionButton').click();
        cy.get(this.optionsField).select(value);
    };

    openFindingsAccordion() {
        cy.get(this.findingsAccordionBtn).as('accordionButton').click();
    };

    checkAuditFindingsCheckbox(findings) {
        cy.get(this.findingsCheckboxId(findings)).check({ force: true }).should('be.checked').and('have.value', findings);
    };

    uncheckAuditFindingsCheckbox(findings) {
        cy.get(this.findingsCheckboxId(findings)).uncheck({ force: true }).should('not.be.checked').and('have.value', findings);
    };

    openDirectFundingAccordion() {
        cy.get(this.directFundingAccordionBtn).as('accordionButton').click();
    };

    checkDirectFundingCheckbox(funding) {
        cy.get(this.directFundingCheckboxId(funding)).check({ force: true }).should('be.checked').and('have.value', funding);
    };

    uncheckDirectFundingCheckbox(funding) {
        cy.get(this.directFundingCheckboxId(funding)).uncheck({ force: true }).should('not.be.checked').and('have.value', funding);
    };

    openMajorProgramAccordion() {
        cy.get(this.majorProgramAccordionBtn).as('accordionButton').click();
    };

    checkMajorProgramRadio(value) {
        cy.get(`${this.majorProgramRadio}[value="${value}"]`).check({ force: true }).should('be.checked').and('have.value', value);
    };

    uncheckMajorProgramRadio(value) {
        cy.get(`${this.majorProgramRadio}[value="${value}"]`).check({ force: true }).should('be.checked').and('have.value', value);
    };

    openAndSelectFyEndMonth(value) {
        cy.get(this.fiscalYearEndMonthBtn).as('accordionButton').click();
        cy.get(this.fyEndMonth).select(value);
    };

    openAndSelectEntityTypeCheckbox(entity) {
        cy.get(this.entityTypeBtn).as('accordionButton').click();
        cy.get(this.entityTypeCheckboxId(entity)).check({ force: true }).should('be.checked').and('have.value', entity);
    };

    testReportId(value) {
        cy.get(this.reportdIdAccordionBtn).as('accordionButton').click();
        cy.get(this.reportIdField).clear().type(value);
    };

    testTypeRequirement(value) {
        cy.get(this.typeRequirementBtn).as('accordionButton').click();
        cy.get(this.typeRequirementField).clear().type(value);
    };

    testSearchSubmitButton() {
        cy.get(`${this.searchSubmitBtn}:last`).click();
    };

    testSearchTable() {
        cy.get(this.searchTable).should('exist');
        cy.contains('td', 'D7A4J33FUMJ1')
            .siblings()
            .find('a.usa-link[href^="/dissemination/summary"]')
            .should('have.attr', 'target', '_blank')
            .invoke('removeAttr', 'target')
            .click()

        cy.url().should('include', '/dissemination/summary');
    };

    testAdvSearch() {
        cy.get(this.advanceSearchBtn).should('contain', 'advanced search').click();
    };

    testSummaryReport() {
        cy.url().then(url => {
            const reportId = url.split('/').pop();
            cy.url().should('include', `/dissemination/summary/${reportId}`);
            cy.get(this.sfSacDownloadBtn).should('exist').click();
            //single audit report pdf may not appear for certain audits
            //cy.get(this.singleAuditBtn).should('exist').click();
            cy.wait(5000);
            this.testSfSacDownload(url);
            //this.testSumReportDownload(url);
        });
    };

    testSfSacDownload(url) {
        const reportId = url.split('/').pop();
        const downloadUrl = Cypress.config().baseUrl + `/dissemination/summary/${reportId}`
        cy.downloadFile(downloadUrl,
            'cypress/downloads', '2022-12-GSAFAC-0000000001.xlsx');
    };
    testSumReportDownload(url) {
        const reportId = url.split('/').pop();
        const downloadUrl = Cypress.config().baseUrl + `/dissemination/summary/${reportId}`
        cy.downloadFile(downloadUrl,
            'cypress/downloads', '2022-12-GSAFAC-0000000001.pdf');
    };
};

export default searchPage;