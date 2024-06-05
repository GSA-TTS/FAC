import { testInitializeAudit } from './initialize-audit.js';
import {
  testWorkbookFederalAwards,
} from './workbook-uploads.js';

export function testFederalAwards(isTribal=false) {
  testInitializeAudit(isTribal);

  // Upload all the workbooks. Don't intercept the uploads, which means a file will make it into the DB.
  cy.get(".usa-link").contains("Federal Awards").click();
  testWorkbookFederalAwards(false);
};
