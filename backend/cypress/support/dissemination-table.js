/*
  Re-useable code for testing the dissemination table.
*/

const API_GOV_JWT = Cypress.env('API_GOV_JWT') || '';
const API_GOV_KEY = Cypress.env('API_GOV_KEY') || '';
const API_GOV_USER_ID_ADMIN = Cypress.env('API_GOV_USER_ID_ADMIN');
const API_GOV_URL = Cypress.env('API_GOV_URL');
const API_VERSION = Cypress.env('API_VERSION');
const ADMIN_API_VERSION = Cypress.env('ADMIN_API_VERSION');

const requestOptions = {
  method: 'GET',
  url: `${API_GOV_URL}/general`,
  headers: {
    Authorization: `Bearer ${API_GOV_JWT}`,
    'X-Api-Key': API_GOV_KEY,
  },
}

function grantTribalAccess(email, user_id) {
  // use admin user to grant tribal access to user
  cy.request({
    method: 'POST',
    url: `${API_GOV_URL}/rpc/add_tribal_api_key_access`,
    headers: {
      Authorization: `Bearer ${API_GOV_JWT}`,
      'X-Api-Key': API_GOV_KEY,
      'X-Api-User-Id': API_GOV_USER_ID_ADMIN,
      'Content-Profile': ADMIN_API_VERSION,
      'Content-Type': 'application/json',
      'Prefer': 'params=single-object',
    },
    body: {
      "email": `${email}`,
      "key_id": `${user_id}`,
    }
  }).should((response) => {
    expect(response.body).to.equal(true);
  });
}

function revokeTribalAccess(email, user_id) {
  // use admin user to revoke tribal access to user
  cy.request({
    method: 'POST',
    url: `${API_GOV_URL}/rpc/remove_tribal_api_key_access`,
    headers: {
      Authorization: `Bearer ${API_GOV_JWT}`,
      'X-Api-Key': API_GOV_KEY,
      'X-Api-User-Id': API_GOV_USER_ID_ADMIN,
      'Content-Profile': ADMIN_API_VERSION,
      'Content-Type': 'application/json',
      'Prefer': 'params=single-object',
    },
    body: {
      "email": `${email}`,
      "key_id": `${user_id}`,
    }
  }).should((response) => {
    expect(response.body).to.equal(true);
  });
}

export function testReportIdNotFoundWithoutTribalAccess(reportId) {
  cy.request({
    ...requestOptions,
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(0);
  });
}

export function testReportIdFoundWithoutTribalAccess(reportId) {
  cy.request({
    ...requestOptions,
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(1);
    const hasAgency = response.body[0]?.cognizant_agency || response.body[0]?.oversight_agency;
    expect(Boolean(hasAgency)).to.be.true;
  });
}

export function testReportIdFoundWithTribalAccess(reportId) {
  const tribal_access_email = `${crypto.randomUUID()}@example.com`;
  const tribal_access_user_id = crypto.randomUUID();

  grantTribalAccess(tribal_access_email, tribal_access_user_id);
  
  // try to pull the tribal, non-public data from the API using the (now) privileged user
  cy.request({
    method: 'GET',
    url: `${API_GOV_URL}/general`,
    headers: {
      Authorization: `Bearer ${API_GOV_JWT}`,
      'X-Api-Key': API_GOV_KEY,
      'X-Api-User-Id': tribal_access_user_id,
      'Accept-Profile': API_VERSION
    },
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(1);
    const hasAgency = response.body[0]?.cognizant_agency || response.body[0]?.oversight_agency;
    expect(Boolean(hasAgency)).to.be.true;
  });

  revokeTribalAccess(tribal_access_email, tribal_access_user_id);
}

export function testReportIdNotFoundWithTribalAccess(reportId) {
  const tribal_access_email = `${crypto.randomUUID()}@example.com`;
  const tribal_access_user_id = crypto.randomUUID();

  grantTribalAccess(tribal_access_email, tribal_access_user_id);
  
  // try to pull the tribal, non-public data from the API using the (now) privileged user
  cy.request({
    method: 'GET',
    url: `${API_GOV_URL}/general`,
    headers: {
      Authorization: `Bearer ${API_GOV_JWT}`,
      'X-Api-Key': API_GOV_KEY,
      'X-Api-User-Id': tribal_access_user_id,
      'Accept-Profile': API_VERSION
    },
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(0);
  });

  revokeTribalAccess(tribal_access_email, tribal_access_user_id);
}
