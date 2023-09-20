/*
  Re-useable code for testing the dissemination table.
*/

const API_GOV_JWT = Cypress.env('API_GOV_JWT');

export function testReportId(reportId, numExpectedResults) {
  cy.request({
    method: 'GET',
    url: 'localhost:3000/general',
    headers: {
    Authorization: `Bearer ${API_GOV_JWT}`,
    },
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(numExpectedResults);
  });
}
