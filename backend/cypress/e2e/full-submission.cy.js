import { testFullSubmission } from '../support/full-submission.js';

describe('Full audit submissions', () => {
  it('Non-tribal, public', () => {
    testFullSubmission(false, true);
  });

  it('Tribal, public', () => {
    testFullSubmission(true, true);
  });

  it('Tribal, non-public', () => {
    testFullSubmission(true, false);
  });
});
