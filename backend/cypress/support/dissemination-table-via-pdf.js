/*
  Re-useable code for testing the dissemination table.
*/

// We're testing a 2x2. Actually, this would be better as a table, as this is a 3D test.
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

// This could be reworked into a table test.
// However, the tests below should be clear
// enough to not require a full re-working.

// Where
// T = Tribal(1)/Not Tribal(0)
// P = Private(1)/Public(0)
// U = Privileged(1)/Unprivileged(0)
// L = Length expected

// T P U L
// -------
// 0 0 0 1
// 0 0 1 1
// 0 1 0 -
// 0 1 1 -
// 1 0 0 1
// 1 0 1 1
// 1 1 0 0
// 1 1 1 1



export function testSubmissionAccessViaPDF(reportId, isTribal, isPublic) {  
  console.log(`reportId: ${reportId}, isTribal: ${isTribal}, isPublic: ${isPublic}`);

  // The audit IS tribal and IS public
  ////////////////////////////////////////
  if (isTribal && isPublic) {
    // When it is Tribal and public, we should always
    // find the report id in the public and private endpoints
    expect(isTribal).to.be.true
    expect(isPublic).to.be.true
    // We should be able to grab the PDF by URL
    // https://app.fac.gov/dissemination/report/pdf/2023-04-GSAFAC-0000050825
    cy.request({
      method: 'GET',
      url: '/dissemination/report/pdf/' + reportId
    }).should((response) => {
      expect(response.isOkStatusCode).to.equal(true);
    });
  }
  ////////////////////////////////////////
  // The audit IS tribal and IS NOT public
  ////////////////////////////////////////
  else if (isTribal && !isPublic) {
    expect(isTribal).to.be.true
    expect(isPublic).to.be.false
    cy.request({
      method: 'GET',
      url: '/dissemination/report/pdf/' + reportId,
      failOnStatusCode: false,
    }).should((response) => {
      expect(response.isOkStatusCode).to.equal(false);
    });

  }
  ////////////////////////////////////////
  // The audit IS NOT tribal and IS public
  ////////////////////////////////////////
  else if (!isTribal && isPublic) {
    // This is a standard audit.
    expect(isTribal).to.be.false
    expect(isPublic).to.be.true
    // We should always find it in all endpoints, priv or unpriv.
    cy.request({
      method: 'GET',
      url: '/dissemination/report/pdf/' + reportId
    }).should((response) => {
      expect(response.isOkStatusCode).to.equal(true);
    });
  }
  ////////////////////////////////////////
  // The audit IS NOT tribal and IS NOT public
  // (This is not possible.)
  ////////////////////////////////////////
  else if (!isTribal && !isPublic) {
    console.log("Unreachable test case in testTribalAccess");
    expect(true).to.be.false;
  }
  ////////////////////////////////////////
  // The audit somehow is none of the above.
  // (This is not possible.)
  ////////////////////////////////////////
  else {
    // We really should never be here.
    console.log("The universe broke in testTribalAccess");
    expect(false).to.be.true;
  };
};
