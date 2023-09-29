describe('Display my audit submissions', () => {
  before(() => {
    cy.visit('/submissions');
  });
  describe('On correct page.', () => {
    it('does not display the submissions table', () => {
      cy.get('h1').should('have.text', 'My audit submissions');
    });
  });

  describe('Do not display table if user has no submissions', () => {
    it('does not display the submissions table', () => {
      cy.intercept(
        {
          method: 'GET',
          url: 'https://fac-dev.app.cloud.gov/submissions',
        },
        { body: [] }
      ).as('hasNoData');
      cy.visit('/submissions/');
      cy.wait('@hasNoData').then((interception) => {
        // console.log(interception);
        cy.get('.usa-table-container')
          .should('have.attr', 'class')
          .and('contain', 'display-none');
      });
    });
  });

  describe('Display table if user has submissions', () => {
    it('displays the submissions table', () => {
      cy.intercept(
        {
          method: 'GET',
          url: 'https://fac-dev.app.cloud.gov/submissions',
        },
        [
          {
            report_id: '2021FQF0001000003',
            submission_status: 'in_progress',
            auditee_uei: 'MQGVHJH74DW7',
            auditee_fiscal_period_end: '2022-01-01',
            auditee_name: 'Test 1',
          },
          {
            report_id: '20215L30001000005',
            submission_status: 'in_progress',
            auditee_uei: 'XRGSHJH74DW7',
            auditee_fiscal_period_end: '2022-01-01',
            auditee_name: 'Test 2',
          },
          {
            report_id: '2021JG70001000010',
            submission_status: 'in_progress',
            auditee_uei: 'ZQGGHJH74xW7',
            auditee_fiscal_period_end: '2022-01-01',
            auditee_name: 'INTERNATIONAL BUSINESS MACHINES CORPORATION',
          },
        ]
      ).as('hasData');
      cy.visit('/submissions/');
      cy.wait('@hasData').then((interception) => {
        assert.isNotNull(interception.response.body, 'has data');
        cy.get('.usa-table-container')
          .should('have.attr', 'class')
          .and('not.contain', 'display-none');
      });
    });
  });

  describe('Sorted by Report ID ASC', () => {
    it('TH should have sorted attr set to ascending', () => {
      cy.get('#report_id')
        .should('have.attr', 'aria-sort')
        .and('contain', 'ascending');
    });
    it('TH should have visible ascending icon', () => {
      cy.get('#report_id svg .ascending').should(
        'have.css',
        'fill',
        'rgb(27, 27, 27)'
      );
    });
  });

  describe('Displays modal on click', () => {
    it('should display modal on click', () => {
      cy.get('th .usa-link').contains('UEI').click();
      cy.get('.usa-modal-wrapper')
        .should('have.attr', 'class')
        .and('contain', 'is-visible');
    });

    it('should display modal on click', () => {
      cy.get('li .usa-button').contains('Close').click();
      cy.get('.usa-modal-wrapper')
        .should('have.attr', 'class')
        .and('contain', 'is-hidden');
    });
  });
});
