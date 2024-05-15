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
    };

    downloadSumReport(url) {
        const reportId = url.split('/').pop();
        const downloadUrl = Cypress.config().baseUrl + `/dissemination/summary/${reportId}`
        this.elements.singleAuditBtn().click();
        cy.downloadFile(downloadUrl,
            'cypress/downloads', '2022-12-GSAFAC-0000000001.pdf');
    };
};

export default searchPage;