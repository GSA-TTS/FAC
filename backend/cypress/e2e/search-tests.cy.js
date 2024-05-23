import searchPage from '../page_objects/search-page.js';
import searchDataJson from '../fixtures/search_data.json'

let search;
const searchData = searchDataJson;

beforeEach(() => {
  cy.visit('/dissemination/search/');

  search = new searchPage();

  search.elements.advanceSearchBtn().should('contain', 'advanced search').click();
});

describe('Test Basic Search Fields', () => {

  it('Tests Audit Year Checkbox', () => {
    const year = searchData.yearsToCheck[0];
    search.elements.yearCheckboxById(year)
      .check({ force: true })
      .should('be.checked')
      .and('have.value', year)
  });

  it('Tests UEI or EIN Field ', () => {
    const ueiOrEinValue = searchData.ueiOrein;
    search.elements.ueiOrEinField().clear().type(ueiOrEinValue)
      .should('have.value', ueiOrEinValue);
  });

  it('Tests Name Field', () => {
    const nameValue = searchData.name;
    search.elements.entityNameAccordionBtn().contains('Name (Entity, Auditee, or Auditor)').click();
    search.elements.entityNameField().clear().type(nameValue)
      .should('have.value', nameValue);
  });

  it('Tests FAC Acceptance Date Field', () => {
    const startDate = searchData.accDate[0]
    const endDate = searchData.accDate[1];
    search.elements.facAcceptDateAccordionBtn().contains('FAC acceptance date').as('accordionButton').click();
    search.elements.startDateField().clear().type(startDate);
    search.elements.endDateField().clear().type(endDate);
  });

  it('Tests State Field', () => {
    const stateValue = searchData.state;
    search.elements.stateAccordionBtn().contains('State').as('accordionButton').click();
    search.elements.auditeeState().select(stateValue).should('have.value', stateValue);
  });

  it('Tests Fiscal Year End Month Field', () => {
    const fyEndMonthValue = searchData.fiscalYearEndMonth;
    search.elements.fiscalYearEndMonthBtn().contains('Fiscal year end month').as('accordionButton').click();
    search.elements.fyEndMonth().select(fyEndMonthValue).should('have.value', fyEndMonthValue);
  });

  it('Tests Entity Type Field', () => {
    const entityValue = searchData.entityType;
    search.elements.entityTypeAccordionBtn().contains('Entity type').as('accordionButton').click();
    search.elements.entityTypeCheckboxId(entityValue).check({ force: true }).should('be.checked').and('have.value', entityValue);
  });

  it('Tests ReportId Field', () => {
    const reportIdValue = searchData.reportId
    search.elements.reportdIdAccordionBtn().as('accordionButton').click();
    search.elements.reportIdField().clear().type(reportIdValue).should('have.value', reportIdValue);
    search.clickSearchSubmitButton();
    cy.url().should('include', '/dissemination/search/');
  });

  it('Clicks Submit Button', () => {
    search.clickSearchSubmitButton();
    cy.url().should('include', '/dissemination/search/');
  });
});

describe('Test Advance Search Fields', () => {

  it('Tests Audit Year Checkbox', () => {
    const year = searchData.yearsToCheck[0];
    search.elements.yearCheckboxById(year)
      .check({ force: true })
      .should('be.checked')
      .and('have.value', year)
  });

  it('Tests UEI or EIN Field ', () => {
    const ueiOrEinValue = searchData.ueiOrein;
    search.elements.ueiOrEinField().clear().type(ueiOrEinValue)
      .should('have.value', ueiOrEinValue);
  });

  it('Tests ALN Field ', () => {
    const alnValue = searchData.aln;
    search.elements.alnAccordionBtn().contains('Assistance Listing Number (formerly CFDA').as('accordionButton').click();
    search.elements.alnField().clear().type(alnValue);
  });

  it('Tests Name Field', () => {
    const nameValue = searchData.name;
    search.elements.entityNameAccordionBtn().contains('Name (Entity, Auditee, or Auditor)').click();
    search.elements.entityNameField().clear().type(nameValue)
      .should('have.value', nameValue);
  });

  it('Tests FAC Acceptance Date Field', () => {
    const startDate = searchData.accDate[0]
    const endDate = searchData.accDate[1];
    search.elements.facAcceptDateAccordionBtn().contains('FAC acceptance date').as('accordionButton').click();
    search.elements.startDateField().clear().type(startDate);
    search.elements.endDateField().clear().type(endDate);
  });

  it('Tests State Field', () => {
    const stateValue = searchData.state;
    search.elements.stateAccordionBtn().contains('State').as('accordionButton').click();
    search.elements.auditeeState().select(stateValue).should('have.value', stateValue);
  });

  it('Tests Cog or Over Field', () => {
    const cogOrOverOrEitherOptions = searchData.cogOrover[0];
    search.elements.cogOrOverAccordionBtn().contains('Cognizant or Oversight').as('accordionButton').click();
    search.elements.optionsField().select(cogOrOverOrEitherOptions);
  });

  it('Tests Audit Findings Field', () => {
    const findingsValue = searchData.findings[0];
    search.elements.auditFindingsAccordionBtn().contains('Audit findings').as('accordionButton').click();
    search.elements.findingsCheckboxId(findingsValue)
      .check({ force: true })
      .should('be.checked')
      .and('have.value', findingsValue);
  });

  it('Tests Direct Funding Field', () => {
    const fundingValue = searchData.directFunding[0];
    search.elements.directFundingAccordionBtn().contains('Direct funding').as('accordionButton').click();
    search.elements.directFundingCheckboxId(fundingValue)
      .check({ force: true })
      .should('be.checked')
      .and('have.value', fundingValue);
  });

  it('Tests Major Program Field', () => {
    const majorProgramValue = searchData.majorProgram[0];
    search.elements.majorProgramAccordionBtn().contains('Major program').as('accordionButton').click();
    search.elements.majorProgramRadio(majorProgramValue)
      .check({ force: true })
      .should('be.checked')
      .and('have.value', majorProgramValue)
  });

  it('Tests Fiscal Year End Month Field', () => {
    const fyEndMonthValue = searchData.fiscalYearEndMonth;
    search.elements.fiscalYearEndMonthBtn().contains('Fiscal year end month').as('accordionButton').click();
    search.elements.fyEndMonth().select(fyEndMonthValue).should('have.value', fyEndMonthValue);
  });

  it('Tests Type Requirement', () => {
    const typeValue = searchData.typeRequirement;
    search.elements.typeRequirementAccordionBtn().contains('Type Requirement').as('accordionButton').click();
    search.elements.typeRequirementField().clear().type(typeValue);
  });

  it('Tests Entity Type Field', () => {
    const entityValue = searchData.entityType;
    search.elements.entityTypeAccordionBtn().contains('Entity type').as('accordionButton').click();
    search.elements.entityTypeCheckboxId(entityValue).check({ force: true }).should('be.checked').and('have.value', entityValue);
  });

  it('Tests Passthrough Name Field', () => {
    const passthroughValue = searchData.passthroughName;
    search.elements.passThroughNameAccordionBtn().contains('Passthrough Name').as('accordionButton').click();
    search.elements.passThroughNameField().clear().type(passthroughValue);
  });

  it('Tests ReportId Field', () => {
    const reportIdValue = searchData.reportId
    search.elements.reportdIdAccordionBtn().as('accordionButton').click();
    search.elements.reportIdField().clear().type(reportIdValue).should('have.value', reportIdValue);
    search.clickSearchSubmitButton();
    cy.url().should('include', '/dissemination/search/');
  });

  it('Clicks Submit Button', () => {
    search.clickSearchSubmitButton();
    cy.url().should('include', '/dissemination/search/');
  });
});

describe('Test search and return results', () => {
  it('Fills out basic search fields and downloads summary report', () => {

    search.elements.yearCheckboxById(searchData.yearsToCheck[0])
      .check({ force: true })
      .should('be.checked')
      .and('have.value', searchData.yearsToCheck[0]);

    search.elements.ueiOrEinField().clear().type(searchData.ueiOrein)
      .should('have.value', searchData.ueiOrein);

    search.elements.entityNameAccordionBtn().contains('Name (Entity, Auditee, or Auditor)').click();
    search.elements.entityNameField().clear().type(searchData.name)
      .should('have.value', searchData.name);

    search.elements.facAcceptDateAccordionBtn().contains('FAC acceptance date').as('accordionButton').click();
    search.elements.startDateField().clear().type(searchData.accDate[0]);
    search.elements.endDateField().clear().type(searchData.accDate[1]);

    search.elements.stateAccordionBtn().contains('State').as('accordionButton').click();
    search.elements.auditeeState().select(searchData.state).should('have.value', searchData.state);

    search.elements.fiscalYearEndMonthBtn().contains('Fiscal year end month').as('accordionButton').click();
    search.elements.fyEndMonth().select(searchData.fiscalYearEndMonth).should('have.value', searchData.fiscalYearEndMonth);

    search.elements.entityTypeAccordionBtn().contains('Entity type').as('accordionButton').click();
    search.elements.entityTypeCheckboxId(searchData.entityType).check({ force: true }).should('be.checked').and('have.value', searchData.entityType);

    search.elements.reportdIdAccordionBtn().as('accordionButton').click();
    search.elements.reportIdField().clear().type(searchData.reportId)
      .should('have.value', searchData.reportId);

    search.clickSearchSubmitButton();
    cy.url().should('include', '/dissemination/search/');

    search.elements.searchTable().should('exist');
    cy.contains('td', 'D')
      .siblings()
      .find('a.usa-link[href^="/dissemination/summary"]')
      .should('have.attr', 'target', '_blank')
      .invoke('removeAttr', 'target')
      .click();

    cy.url().should('include', '/dissemination/summary');

    cy.url().then(url => {
      search.downloadSfSac(url);
    });
  });
});

describe('Test Reset Search Button', () => {
  it('Fills out basic search fields and clicks reset button', () => {
    search.elements.yearCheckboxById(searchData.yearsToCheck[0])
      .check({ force: true })
      .should('be.checked')
      .and('have.value', searchData.yearsToCheck[0]);

    search.elements.ueiOrEinField().clear().type(searchData.ueiOrein)
      .should('have.value', searchData.ueiOrein);

    search.elements.entityNameAccordionBtn().contains('Name (Entity, Auditee, or Auditor)').click();
    search.elements.entityNameField().clear().type(searchData.name)
      .should('have.value', searchData.name);

    search.elements.facAcceptDateAccordionBtn().contains('FAC acceptance date').as('accordionButton').click();
    search.elements.startDateField().clear().type(searchData.accDate[0]);
    search.elements.endDateField().clear().type(searchData.accDate[1]);

    search.elements.stateAccordionBtn().contains('State').as('accordionButton').click();
    search.elements.auditeeState().select(searchData.state).should('have.value', searchData.state);

    search.elements.fiscalYearEndMonthBtn().contains('Fiscal year end month').as('accordionButton').click();
    search.elements.fyEndMonth().select(searchData.fiscalYearEndMonth).should('have.value', searchData.fiscalYearEndMonth);

    search.elements.entityTypeAccordionBtn().contains('Entity type').as('accordionButton').click();
    search.elements.entityTypeCheckboxId(searchData.entityType).check({ force: true }).should('be.checked').and('have.value', searchData.entityType);

    search.elements.reportdIdAccordionBtn().as('accordionButton').click();
    search.elements.reportIdField().clear().type(searchData.reportId)
      .should('have.value', searchData.reportId);

    search.clickResetButton();

    search.elements.yearCheckboxById(searchData.yearsToCheck[1]).should('not.be.checked');
    search.elements.ueiOrEinField().should('have.value', '');
    search.elements.entityNameField().should('have.value', '');
    search.elements.startDateField().should('have.value', '');
    search.elements.endDateField().should('have.value', '');
    search.elements.reportIdField().should('have.value', '');
  });
});




