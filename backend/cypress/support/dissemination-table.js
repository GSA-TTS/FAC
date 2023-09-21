/*
  Re-useable code for testing the dissemination table.
*/

const API_GOV_JWT = Cypress.env('API_GOV_JWT') || '';
const API_GOV_KEY = Cypress.env('API_GOV_KEY') || '';
const API_GOV_URL = Cypress.env('API_GOV_URL');

export function testReportId(reportId, expectedResults) {
  cy.request({
    method: 'GET',
    url: `${API_GOV_URL}/general`,
    headers: {
        Authorization: `Bearer ${API_GOV_JWT}`,
        'X-Api-Key': API_GOV_KEY,
    },
    qs: {report_id: `eq.${reportId}`},
    }).should((response) => {
      expect(response.body).to.have.length(expectedResults);
  });
}
