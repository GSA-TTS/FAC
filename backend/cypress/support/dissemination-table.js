/*
  Re-useable code for testing the dissemination table.
*/

const API_GOV_JWT = Cypress.env('API_GOV_JWT') || '';
const API_GOV_KEY = Cypress.env('API_GOV_KEY') || '';
const API_GOV_USER_ID = Cypress.env('API_GOV_USER_ID');
const API_GOV_KEY_ADMIN = Cypress.env('API_GOV_KEY_ADMIN');
const API_GOV_USER_ID_ADMIN = Cypress.env('API_GOV_USER_ID_ADMIN');
const API_GOV_URL = Cypress.env('API_GOV_URL');
const API_VERSION = Cypress.env('API_VERSION');
const ADMIN_API_VERSION = Cypress.env('ADMIN_API_VERSION');

function apiRequestOptions(endpoint) {
  return {
    method: 'GET',
    url: `${API_GOV_URL}/${endpoint}`,
    headers: {
      'Authorization': `Bearer ${API_GOV_JWT}`,
      'X-Api-Key': API_GOV_KEY,
      'Accept-Profile': API_VERSION,
      'X-Api-User-Id': API_GOV_USER_ID,
    },
  };
};

const tribalAdminApiHeaders = {
  'Authorization': `Bearer ${API_GOV_JWT}`,
  'X-Api-Key': API_GOV_KEY_ADMIN,
  'X-Api-User-Id': API_GOV_USER_ID_ADMIN,
  'Content-Profile': ADMIN_API_VERSION,
  'Content-Type': 'application/json',
  'Prefer': 'params=single-object',
};

function grantTribalAccess(email, user_id) {
  // use admin user to grant tribal access to user
  cy.request({
    method: 'POST',
    url: `${API_GOV_URL}/rpc/add_tribal_api_key_access`,
    headers: {
      ...tribalAdminApiHeaders,
    },
    body: {
      "email": `${email}`,
      "key_id": `${user_id}`,
    }
  }).should((response) => {
    expect(response.body.result).to.equal("success");
  });
  console.log(`Granted access to ${email} and ${user_id}`)

}

function revokeTribalAccess(email, user_id) {
  // use admin user to revoke tribal access to user
  cy.request({
    method: 'POST',
    url: `${API_GOV_URL}/rpc/remove_tribal_api_key_access`,
    headers: {
      ...tribalAdminApiHeaders
    },
    body: {
      "email": `${email}`,
      "key_id": `${user_id}`,
    }
  }).should((response) => {
    expect(response.body.result).to.equal("success");
  });
  console.log(`Revoked access for ${email} and ${user_id}`)

}


// We're testing a 2x2.
//                    is tribal                           is not tribal             
//           ┌────────────────────────────────┬────────────────────────────────┐    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
//  public   │    UNPRIVILEGED KEY OK         │        UNPRIVILEGED KEY OK     │    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
//           ├────────────────────────────────┼────────────────────────────────┤    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
// private   │     PRIV KEY OK / UNPRIV NO    │       DOES NOT COMPUTE         │    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
//           │                                │                                │    
//           └────────────────────────────────┴────────────────────────────────┘    

const public_endpoints = [
  "general", 
  "federal_awards", 
  "findings", 
  "additional_ueis",
  // "passthrough",
  "secondary_auditors",
  // "additional_eins"
];
const private_endpoints = [
  "findings_text", 
  "corrective_action_plans", 
  "notes_to_sefa",
];


export function testSubmissionAccess(reportId, isTribal, isPublic) {
  console.log(`reportId: ${reportId}, isTribal: ${isTribal}, isPublic: ${isPublic}`);

  if (isTribal && isPublic) {
    // When it is Tribal and public, we should always
    // find the report id in the public and private endpoints
    expect(isTribal).to.be.true
    expect(isPublic).to.be.true
    for (const ep of public_endpoints.concat(private_endpoints)) {
      testWithUnprivilegedKey(reportId, ep, 1);
      testWithPrivilegedKey(reportId, ep, 1);
    }
  } else if (isTribal && !isPublic) {
    // When it is Tribal, but not public, we need...
    expect(isTribal).to.be.true
    expect(isPublic).to.be.false

    // To always find the report id in public endpoints
    for (const ep of public_endpoints) {
      testWithUnprivilegedKey(reportId, ep, 1);
      testWithPrivilegedKey(reportId, ep, 1);
    }

    // To *not* find the report id in private endpoints
    // when we have an unprivileged key, but we should
    // find it there when we have a privileged key.
    for (const ep of private_endpoints) {
      testWithUnprivilegedKey(reportId, ep, 0);
      testWithPrivilegedKey(reportId, ep, 1);
    }
  } else if (!isTribal && isPublic) {
    // This is a standard audit.
    expect(isTribal).to.be.false
    expect(isPublic).to.be.true
    // We should always find it in all endpoints, priv or unpriv.
    for (const ep of public_endpoints.concat(private_endpoints)) {
      testWithUnprivilegedKey(reportId, ep, 1);
      testWithPrivilegedKey(reportId, ep, 1);
    }
  } else if (!isTribal && !isPublic) {
    // This should not be possible, and should fail.
    console.log("Unreachable test case in testTribalAccess");
    expect(true).to.be.false;
  } else {
    // We really should never be here.
    console.log("The universe broke in testTribalAccess");
    expect(false).to.be.true;
  }
}

export function testWithUnprivilegedKey(reportId, endpoint, expected_length) {
  console.log(`unpriv reportId: ${reportId}, endpoint: ${endpoint}, len: ${expected_length}`)
  cy.request({
    ...apiRequestOptions(endpoint),
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(expected_length);
  });

  if (expected_length > 0) {
    cy.request({
      ...apiRequestOptions('general'),
      qs: {report_id: `eq.${reportId}`},
    }).should((response) => {
      const hasAgency = response.body[0]?.cognizant_agency || response.body[0]?.oversight_agency;
      expect(Boolean(hasAgency)).to.be.true;  
      });  
  }
}

export function testWithPrivilegedKey(reportId, endpoint, expected_length) {
  console.log(`priv reportId: ${reportId}, endpoint: ${endpoint}, len: ${expected_length}`)
  // First grant access to this key
  const tribal_access_email = `${crypto.randomUUID()}@example.com`;
  const tribal_access_user_id = API_GOV_USER_ID;
  grantTribalAccess(tribal_access_email, tribal_access_user_id);
  // Do the request
  cy.request({
    ...apiRequestOptions(endpoint),
    qs: {report_id: `eq.${reportId}`},
  }).should((response) => {
    expect(response.body).to.have.length(expected_length);
  });

  if (expected_length > 0) {
    cy.request({
      ...apiRequestOptions('general'),
      qs: {report_id: `eq.${reportId}`},
    }).should((response) => {
      const hasAgency = response.body[0]?.cognizant_agency || response.body[0]?.oversight_agency;
      expect(Boolean(hasAgency)).to.be.true;  
      });  
  }
  revokeTribalAccess(tribal_access_email, tribal_access_user_id);
}

