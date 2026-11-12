class searchPage {
    //encapsulate page elements within a elements object
    elements = {
        alnAccordionBtn: () => cy.get('.usa-accordion__button:contains("Assistance Listing Numbers (formerly CFDAs")'),
        alnField: () => cy.get('#alns'),
        auditeeState: () => cy.get('#auditee_state'),
        auditFindingsAccordionBtn: () => cy.get('.usa-accordion__button:contains("Audit findings")'),
        cogOrOverAccordionBtn: () => cy.get('.usa-accordion__button:contains("Cognizant or Oversight")'),
        directFundingAccordionBtn: () => cy.get('.usa-accordion__button:contains("Direct funding")'),
        directFundingCheckbox: () => cy.get('#usa-checkbox__input[value="${value}"]'),
        directFundingCheckboxId: (funding) => cy.get(`.usa-checkbox__input[value="${funding.toLowerCase()}"]`),
        endDateField: () => cy.get('#end_date'),
        entityNameAccordionBtn: () => cy.get('.usa-accordion__button:contains("Names (Entity, Auditee, or Auditor)")'),
        entityNameField: () => cy.get('#input_entity-names'),
        entityTypeAccordionBtn: () => cy.get('.usa-accordion__button:contains("Entity types")'),
        entityTypeCheckboxId: (entity) => cy.get(`.usa-checkbox__input[value="${entity}"]`),
        facAcceptDateAccordionBtn: () => cy.get('.usa-accordion__button:contains("FAC acceptance date")'),
        findingsCheckboxId: (findings) => cy.get(`.usa-checkbox__input[value="${findings.toLowerCase()}"]`),
        fiscalYearEndMonthBtn: () => cy.get('.usa-accordion__button:contains("Fiscal year end month")'),
        fyEndMonth: () => cy.get('#fy_end_month'),
        majorProgramAccordionBtn: () => cy.get('.usa-accordion__button:contains("Major program")'),
        majorProgramRadio: () => cy.get('.usa-radio__input[name="major_program"]'),
        optionsField: () => cy.get('#options'),
        passThroughNameAccordionBtn: () => cy.get('.usa-accordion__button:contains("Passthrough Name")'),
        passThroughNameField: () => cy.get('#passthrough-names'),
        reportdIdAccordionBtn: () => cy.get('.usa-accordion__button:contains("Report ID")'),
        reportId: () => cy.get('.usa-accordion__button:contains("Report ID")'),
        reportIdField: () => cy.get('#input_report-ids'),
        resetBtn: () => cy.get('input.usa-button[type="reset"][value="Reset Search"]'),
        searchSubmitBtn: () => cy.get('input.usa-button[type="submit"][value="Search"]'),
        searchTable: () => cy.get('.usa-table'),
        sfSacDownloadBtn: () => cy.get('a.usa-button p:contains("SF-SAC")'),
        singleAuditBtn: () => cy.get('a.usa-button p:contains("Single audit report")'),
        startDateField: () => cy.get('#start_date'),
        stateAccordionBtn: () => cy.get('.usa-accordion__button:contains("State")'),
        typeRequirementAccordionBtn: () => cy.get('.usa-accordion__button:contains("Type of compliance requirement")'),
        typeRequirementField: () => cy.get('#type-requirements-input'),
        ueiAndEinField: () => cy.get('#input_ueis-and-eins'),
        yearCheckboxById: (year) => cy.get((year.toLowerCase() === 'all_years' ? '#audit-years [id^="audit-years-"]' : `#audit-years-${year}`)),
    };

    clickSearchSubmitButton() {
        this.elements.searchSubmitBtn().last().click();
    };

    clickResetButton() {
        this.elements.resetBtn().last().click();
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
