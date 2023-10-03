/*
  Re-useable code for testing the dissemination table.
*/

const API_GOV_JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBpX2ZhY19nb3YiLCJjcmVhdGVkIjoiMjAyMy0xMC0wMlQxNDowMTo1NS44NzQ0NDEifQ.aKANQ2sy5I3S_wxP8FzhMIv6Kadm_jfxqby58-EkpLM';
const API_GOV_KEY = Cypress.env('API_GOV_KEY') || '';
const API_GOV_URL = Cypress.env('API_GOV_URL');

const requestOptions = {
  method: 'GET',
  url: `${API_GOV_URL}/general`,
  headers: {
    Authorization: `Bearer ${API_GOV_JWT}`,
    'X-Api-Key': API_GOV_KEY,
  },
}

export function testReportIdNotFound(reportId) {
  cy.request({
    ...requestOptions,
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(0);
  });
}

export function testReportIdFound(reportId) {
  cy.request({
    ...requestOptions,
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(1);
    const hasAgency = !!(response.body[0]?.cognizant_agency || response.body[0]?.oversight_agency);
    expect(hasAgency).to.be.true;
  });
}
