import searchPage from '../pageObjects/searchPage.js';

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
  
  cy.fixture('searchPageData/auditYears.json').then((data) => {
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

  cy.fixture('searchPageData/accDate.json').then((data) => {
    accDate = data.accDate;
  })

  cy.fixture('searchPageData/state.json').then((data) => {
    state = data.state;
  })

  cy.fixture('searchPageData/cog-over.json').then((data) => {
    cogOrover = data.cogOrover;
  })

  cy.fixture('searchPageData/auditFindings.json').then((data) => {
    findings = data.findings;
  })

  cy.fixture('searchPageData/directFunding.json').then((data) => {
    directFunding = data.directFunding;
  })

  cy.fixture('searchPageData/majorProgram.json').then((data) => {
    majorProgram = data.majorProgram;
  })

  search = new searchPage();
});

//basic search test
describe('Test Basic Search Fields', () => {
    
    it('checks Audit Years', () => {
      search.checkAuditYearCheckbox('2023');
      search.uncheckAuditYearCheckbox('2023');
      search.checkAllYearsCheckbox('all_years');
      search.testUEIorEin(ueiOrein);
      search.testName(name);
      const [startDate, endDate] = accDate;
        search.testFACacceptanceDate(startDate, endDate);

        search.testState(state);

        search.testSearchSubmitButton();

        search.testSearchTable();


    });


  });