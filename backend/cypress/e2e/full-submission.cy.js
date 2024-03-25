import { testFullSubmission } from '../support/full-submission.js';

describe('Full audit submissions', () => {

  // Test tribal audits first.
  // If these fail, we don't need to proceed.
  it('Tribal, non-public', () => {
    testFullSubmission(true, false);
  });

  it('Tribal, public', () => {
    testFullSubmission(true, true);
  });

  it('Non-tribal, public', () => {
    testFullSubmission(false, true);
  });


});
