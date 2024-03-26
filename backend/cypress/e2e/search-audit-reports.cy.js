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

      describe('Test Audit Year Checkbox', () => {
        it('checks Audit Years', () => {
          search.checkAuditYearCheckbox('2023');
          search.uncheckAuditYearCheckbox('2023');
          yearsToCheck.forEach((year) => {
            search.checkAuditYearCheckbox(year);
          });
          yearsToCheck.forEach((year) => {
            search.uncheckAuditYearCheckbox(year);
          })
        });
      });

      describe('Test UEI or EIN Field', () => {
        it('checks UEI or EIN', () => {
          search.testUEIorEin(ueiOrein);
        });
      });

      describe('Test ALN(CFDA) Field', () => {
        it('checks ALN', () => {
          search.testALN(aln);
        });
      });

      describe('Test Name Field', () => {
        it('checks Name of Entity, Auditee, or Auditor', () => {
          search.testName(name);
        });
      });

      describe('Test FAC Acceptance Date Field', () => {
        it('checks FAC acceptance date', () => {
          const [startDate, endDate] = accDate;
          search.testFACacceptanceDate(startDate, endDate);
        });
      });

      describe('Test State Field', () => {
        it('checks State', () => {
          search.testState(state);
        });
      });

      describe('Test Cog or Over Field', () => {
        it('checks Cog or Over', () => {
          const [cog, over] = cogOrover;
          search.testCogorOver(over);
        });
      });

      describe('Test Audit Findings Checkbox', () => {
        it('checks Audit Findings', () => {
          search.openFindingsAccordion();
          findings.forEach((findings) => {
            search.checkAuditFindingsCheckbox(findings);
          });
          findings.forEach((findings) => {
            search.uncheckAuditFindingsCheckbox(findings);
          })
        });
      });

      describe('Test Direct Funding Field', () => {
        it('checks Direct Funding', () => {
          search.openDirectFundingAccordion();
          directFunding.forEach((funding) => {
            search.checkDirectFundingCheckbox(funding);
          });
          directFunding.forEach((funding) => {
            search.uncheckDirectFundingCheckbox(funding);
          });
        });
      });

      describe('Test Major Program Field', () => {
        it('checks Major Program', () => {
          search.openMajorProgramAccordion();
          const [T, F] = majorProgram;
          search.checkMajorProgramRadio(T);
          search.uncheckMajorProgramRadio(F);
        });
      });

      describe('Test Search Submit', () => {
        it('clicks Search Submit Button', () => {
          search.testSearchSubmitButton();
        });
      });
