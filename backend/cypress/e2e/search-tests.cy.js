import searchPage from '../pageObjects/search-page.js';

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

beforeEach(() => {
  cy.visit('/dissemination/search/');

  cy.fixture('searchPageData/audit-years.json').then((data) => {
    yearsToCheck = data.yearsToCheck;
  })

  cy.fixture('searchPageData/uei-ein.json').then((data) => {
    ueiOrein = data.ueiOrein;
  })

  cy.fixture('searchPageData/aln.json').then((data) => {
    aln = data.aln;
  })

  cy.fixture('searchPageData/name.json').then((data) => {
    name = data.name;
  })

  cy.fixture('searchPageData/acc-date.json').then((data) => {
    accDate = data.accDate;
  })

  cy.fixture('searchPageData/state.json').then((data) => {
    state = data.state;
  })

  cy.fixture('searchPageData/cog-over.json').then((data) => {
    cogOrover = data.cogOrover;
  })

  cy.fixture('searchPageData/audit-findings.json').then((data) => {
    findings = data.findings;
  })

  cy.fixture('searchPageData/direct-funding.json').then((data) => {
    directFunding = data.directFunding;
  })

  cy.fixture('searchPageData/major-program.json').then((data) => {
    majorProgram = data.majorProgram;
  })

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

    //submit button
    search.testSearchSubmitButton();

    //search results
    search.testSearchTable();

    //summary report
    search.testSummaryReport();

  });


});

//advanced search test
// describe('Test Advance Search Fields', () => {

//   it('checks Audit Years', () => {
//     //advanceSearchButton
//     search.testAdvSearch();

//     //audit years
//     search.checkAuditYearCheckbox('2023');
//     search.uncheckAuditYearCheckbox('2023');
//     search.checkAllYearsCheckbox('all_years');

//     //ueiORein
//     search.testUEIorEin(ueiOrein);
//     search.testALN(aln);
//     search.testName(name);

//     //facAcceptanceDate
//     const [startDate, endDate] = accDate;
//     search.testFACacceptanceDate(startDate, endDate);

//     //state
//     search.testState(state);

//     //cogORover
//     const [cog, over] = cogOrover;
//     search.testCogorOver(over);

//     //findings
//     search.openFindingsAccordion();
//     findings.forEach((findings) => {
//       search.checkAuditFindingsCheckbox(findings);
//     });

//     //directFunding
//     search.openDirectFundingAccordion();
//     directFunding.forEach((funding) => {
//       search.checkDirectFundingCheckbox(funding);
//     });

//     //majorProgram
//     search.openMajorProgramAccordion();
//     const [T, F] = majorProgram;
//     search.checkMajorProgramRadio(T);

//     //submit button
//     search.testSearchSubmitButton();

//     //search results
//     search.testSearchTable();

//     //summary report
//     search.testSummaryReport();


//   });


// });

