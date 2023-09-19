/*
  Re-useable code for testing the dissemination table.
*/
export function testReportId(reportId, numExpectedResults) {
  cy.request({
    method: 'GET',
    url: 'localhost:3000/general',
    headers: {
    Authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBpX2ZhY19nb3YiLCJjcmVhdGVkIjoiMjAyMy0wOS0xOVQxMDowMToxMi4zNTkzNTEifQ.uHOTzHp7sN_8tLftFYcva-5m6CQMrauY0DyIPAIZXpw',
    },
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(numExpectedResults);
  });
}
