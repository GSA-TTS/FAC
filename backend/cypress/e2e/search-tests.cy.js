import searchPage from '../page_objects/search-page.js';
import searchData from '../fixtures/search_page_data/search_data.json'

let search;
let yearsToCheck;
let ueiOrein;
let aln;
let name;
let accDate;
let state;
let cogOrover;
let findings;
let directFunding;
let majorProgram;
let fiscalYearEndMonth;
let typeRequirement;
let entityType;
let passthroughName;
let reportId;

beforeEach(() => {
  cy.visit('/dissemination/search/');

  yearsToCheck = searchData.yearsToCheck;
  ueiOrein = searchData.ueiOrein;
  aln = searchData.aln;
  name = searchData.name;
  accDate = searchData.accDate;
  state = searchData.state;
  cogOrover = searchData.cogOrover;
  findings = searchData.findings;
  directFunding = searchData.directFunding;
  majorProgram = searchData.majorProgram;
  fiscalYearEndMonth = searchData.fiscalYearEndMonth;
  typeRequirement = searchData.typeRequirement;
  entityType = searchData.entityType;
  passthroughName = searchData.passthroughName;
  reportId = searchData.reportId;


  search = new searchPage();
});

//basic search test
describe('Test Basic Search Fields', () => {

  it('checks Audit Years', () => {
    //audit years
    search.checkAuditYearCheckbox('2023');
    search.uncheckAuditYearCheckbox('2023');
    search.checkAllYearsCheckbox('all_years');

    //ueiORein
    search.testUEIorEin(ueiOrein);

    //name
    search.testName(name);

    //facAcceptanceDate
    const [startDate, endDate] = accDate;
    search.testFACacceptanceDate(startDate, endDate);

    //state
    search.testState(state);

    //fyEndMonth
    search.openAndSelectFyEndMonth(fiscalYearEndMonth);

    //entityType
    search.openAndSelectEntityTypeCheckbox(entityType);

    //reportID
    search.testReportId(reportId);

    //submit button
    search.testSearchSubmitButton();

    //search results
    search.testSearchTable();

    //summary report
    search.testSummaryReport();

  });
});

//advanced search test
describe('Test Advance Search Fields', () => {

  it('checks Audit Years', () => {
    //advanceSearchButton
    search.testAdvSearch();

    //audit years
    search.checkAuditYearCheckbox('2023');
    search.uncheckAuditYearCheckbox('2023');
    search.checkAllYearsCheckbox('all_years');

    //ueiORein
    search.testUEIorEin(ueiOrein);
    search.testALN(aln);
    search.testName(name);

    //facAcceptanceDate
    const [startDate, endDate] = accDate;
    search.testFACacceptanceDate(startDate, endDate);

    //state
    search.testState(state);

    //fyEndMonth
    search.openAndSelectFyEndMonth(fiscalYearEndMonth);

    //typeRequirement
    search.testTypeRequirement(typeRequirement);

    //entityType
    search.openAndSelectEntityTypeCheckbox(entityType);

    //reportID
    search.testReportId(reportId);

    //cogORover
    const [either, cog, over] = cogOrover;
    search.testCogorOver(either);

    //findings
    search.openFindingsAccordion();
    findings.forEach((findings) => {
      search.checkAuditFindingsCheckbox(findings);
    });

    //directFunding
    search.openDirectFundingAccordion();
    directFunding.forEach((funding) => {
      search.checkDirectFundingCheckbox(funding);
    });

    //majorProgram
    search.openMajorProgramAccordion();
    const [T, F] = majorProgram;
    search.checkMajorProgramRadio(T);

    //submit button
    search.testSearchSubmitButton();

    //search results
    search.testSearchTable();

    //summary report
    search.testSummaryReport();


  });
});

