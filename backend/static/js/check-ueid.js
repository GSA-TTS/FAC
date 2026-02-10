import { checkValidity } from './validate.js';
import { queryAPI } from './api';

const FORM = document.getElementById('check-eligibility');

// modal-only state
let duplicateReportIds = [];

/**
 * Helpers
 */
function getValue(id) {
  return document.getElementById(id)?.value ?? '';
}

function getTrimmedValue(id) {
  return getValue(id).trim();
}

// FY start is required, so we treat missing/invalid as invalid-year
function parseAuditYearFromFyStart() {
  const raw = getTrimmedValue('auditee_fiscal_period_start');
  if (!raw) return undefined;

  // USWDS date picker often produces MM/DD/YYYY in the visible input
  // Some flows might still give YYYY-MM-DD.
  const iso = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (iso) return Number(iso[1]);

  const mdy = raw.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (mdy) return Number(mdy[3]);

  const parsed = new Date(raw);
  if (!Number.isNaN(parsed.getTime())) return parsed.getFullYear();

  return undefined;
}

function requiredFieldsFilled() {
  return Boolean(
    getTrimmedValue('auditee_uei') &&
      getTrimmedValue('auditee_fiscal_period_start') &&
      getTrimmedValue('auditee_fiscal_period_end')
  );
}

function allResponsesValid() {
  // Your validate.js toggles these classes; gating on any --error presence
  const inputsWithErrors = document.querySelectorAll('[class *="--error"]');
  return inputsWithErrors.length === 0;
}

function setValidateDisabled(shouldDisable) {
  const btn = document.getElementById('continue'); // bottom "Validate UEI" button
  if (btn) btn.disabled = Boolean(shouldDisable);
}

function updateValidateButtonState() {
  // Native required + your custom validation state
  const nativeValid = FORM.checkValidity();
  setValidateDisabled(!(requiredFieldsFilled() && nativeValid && allResponsesValid()));
}

function validatorSupportsField(el) {
  if (!el) return false;

  const id = el.type === 'radio' ? el.name : el.id;
  if (!id) return false;

  // Must have validate-* attributes
  const hasValidateDataset = Object.keys(el.dataset || {}).some((k) =>
    k.toLowerCase().includes('validate')
  );
  if (!hasValidateDataset) return false;

  // Must have the matching error container in the DOM
  return Boolean(document.getElementById(`${id}-error-message`));
}

/**
 * Modal helpers
 */
function resetModal() {
  const modalMain = document.querySelector('#uei-search-result .usa-modal__main');
  const headingEl = modalMain.querySelector('h2');
  const descEl = modalMain.querySelector('#uei-search-result-description');
  const primaryBtn = modalMain.querySelector('button.primary');
  const secondaryBtn = modalMain.querySelector('button.secondary');

  headingEl.textContent = '';
  descEl.innerHTML = '';

  primaryBtn.textContent = '';
  secondaryBtn.textContent = '';

  primaryBtn.onclick = null;
  secondaryBtn.onclick = null;

  document.querySelector('.uei-search-result').classList.add('loading');
}

// 'connection-error' | 'not-found' | 'success' | 'duplicate-submission' | 'invalid-year'
function populateModal(formStatus, auditeeName = '') {
  const auditeeUei = getTrimmedValue('auditee_uei');
  const auditYear = parseAuditYearFromFyStart();

  const modalMain = document.querySelector('#uei-search-result .usa-modal__main');
  const headingEl = modalMain.querySelector('h2');
  const descEl = modalMain.querySelector('#uei-search-result-description');
  const primaryBtn = modalMain.querySelector('button.primary');
  const secondaryBtn = modalMain.querySelector('button.secondary');

  const modalContent = {
    'connection-error': {
      heading: `We can't connect to SAM.gov to confirm your UEI.`,
      description: `
        <dl>
          <dt>UEI you entered</dt>
          <dd>${auditeeUei}</dd>
        </dl>
        <p>We can't proceed without confirming your UEI with SAM.gov. We’re sorry for the delay.</p>
      `,
      buttons: { primary: { text: 'Go back' } },
    },

    success: {
      heading: 'Search Result',
      description: `
        <dl>
          <dt>Unique Entity ID</dt>
          <dd>${auditeeUei}</dd>
          <dt>Auditee name</dt>
          <dd>${auditeeName}</dd>
        </dl>
        <p>Click continue to create a new audit submission for this auditee.</p>
        <p>Not the auditee you’re looking for? Go back, check the UEI you entered, and try again.</p>
      `,
      buttons: { primary: { text: 'Continue' }, secondary: { text: 'Go back' } },
    },

    'not-found': {
      heading: 'Your UEI is not recognized',
      description: `
        <dl>
          <dt>UEI you entered</dt>
          <dd>${auditeeUei}</dd>
        </dl>
        <p>We can't proceed without confirming that you have a valid UEI. We’re sorry for the delay.</p>
        <p>You can try re-entering the UEI. If you don’t have the UEI, you may find it at <a href="https://sam.gov">SAM.gov</a>.</p>
      `,
      buttons: { primary: { text: 'Go back' } },
    },

    'duplicate-submission': {
      heading: 'Are you sure you want to start a new submission?',
      description: `
        <p>We found other submissions that match the UEI and audit year you entered.</p>
        <dl>
          <dt>UEI</dt>
          <dd>${auditeeUei}</dd>
          ${auditYear ? `<dt>Audit year</dt><dd>${auditYear}</dd>` : ''}
        </dl>
      `,
      buttons: { primary: { text: 'Yes, continue' }, secondary: { text: 'No, go back' } },
    },

    'invalid-year': {
      heading: 'Invalid year',
      description: `
        <p>We can't proceed without a valid fiscal period start date (audit year).</p>
        <p>Please enter a valid fiscal period start date and try again.</p>
      `,
      buttons: { primary: { text: 'Go back' } },
    },
  };

  const content = modalContent[formStatus];

  headingEl.textContent = content.heading;
  descEl.innerHTML = content.description;

  // Duplicates list + resubmission nudge
  if (formStatus === 'duplicate-submission') {
    if (duplicateReportIds.length > 0) {
      descEl.innerHTML += `
        <p>These submissions match what you entered:</p>
        <ul>
          ${duplicateReportIds.map((id) => `<li>${id}</li>`).join('')}
        </ul>
      `;
    }
    descEl.innerHTML += `
      <p><strong>Are you sure?</strong> If you meant to correct an already submitted or accepted audit, you may need to resubmit instead.</p>
    `;
  }

// Always set button labels
primaryBtn.textContent = content.buttons.primary.text;
secondaryBtn.textContent = content.buttons.secondary?.text ?? '';

// Button behavior:
primaryBtn.onclick = null;
secondaryBtn.onclick = null;

// Secondary always just closes (template already has data-close-modal)
secondaryBtn.setAttribute('data-close-modal', '');

if (formStatus === 'success' || formStatus === 'duplicate-submission') {
  primaryBtn.removeAttribute('data-close-modal');

  primaryBtn.onclick = (e) => {
    e.preventDefault();
    e.stopPropagation();

    document.querySelector('.uei-search-result')?.classList.remove('is-visible');

    window.setTimeout(() => {
      if (FORM.requestSubmit) {
        FORM.requestSubmit();
      } else {
        FORM.submit();
      }
    }, 0);
  };
} else {
  primaryBtn.setAttribute('data-close-modal', '');
}
}

/**
 * API handlers
 */
function handleUEIDResponse({ valid, response, errors }) {
  // If backend returns duplicates even on "valid: true", treat as duplicate modal
  if (valid && Array.isArray(response?.duplicates) && response.duplicates.length > 0) {
    duplicateReportIds = response.duplicates.map((d) => d.report_id).filter(Boolean);
    populateModal('duplicate-submission', response?.auditee_name ?? '');
    return;
  }

  if (valid) {
    duplicateReportIds = [];
    document.getElementById('auditee_name').value = response.auditee_name;
    populateModal('success', response.auditee_name);
    return;
  }

  // not-found: field errors object
  if (errors && !Array.isArray(errors) && Object.keys(errors).includes('auditee_uei')) {
    populateModal('not-found');
    return;
  }

  // duplicates: errors array includes 'duplicate-submission'
  if (Array.isArray(errors) && errors.includes('duplicate-submission')) {
    duplicateReportIds = Array.isArray(response?.duplicates)
      ? response.duplicates.map((d) => d.report_id).filter(Boolean)
      : [];
    populateModal('duplicate-submission');
    return;
  }

  if (Array.isArray(errors) && errors.includes('invalid-year')) {
    populateModal('invalid-year');
    return;
  }

  populateModal('connection-error');
}

function handleApiError(e) {
  populateModal('connection-error');
  console.error(e);
}

function validateUEID() {
  resetModal();

  const auditee_uei = getTrimmedValue('auditee_uei').toUpperCase();
  document.getElementById('auditee_uei').value = auditee_uei;

  const audit_year = parseAuditYearFromFyStart();
  if (!audit_year) {
    populateModal('invalid-year');
    document.querySelector('.uei-search-result').classList.remove('loading');
    return;
  }

  console.log('UEI validation payload', {
    auditee_uei,
    audit_year,
    fy_start_raw: getTrimmedValue('auditee_fiscal_period_start'),
  });

  queryAPI(
    '/api/sac/ueivalidation',
    { auditee_uei, audit_year },
    { method: 'POST' },
    [handleUEIDResponse, handleApiError]
  );
}

/**
 * FY16 check (keep your existing behavior)
 */
function validateFyStartDate(fyInput) {
  if (!fyInput.value) return;

  const fyFormGroup = document.querySelector('.usa-form-group.validate-fy');
  const fyErrorContainer = document.getElementById('fy-error-message');

  // supports both YYYY-MM-DD and MM/DD/YYYY
  const year = parseAuditYearFromFyStart();
  fyErrorContainer.innerHTML = '';

  if (year && Number(year) < 2016) {
    const errorEl = document.createElement('li');
    errorEl.innerHTML =
      'We are currently only accepting audits from FY16 or later.\
      To submit an audit for a different fiscal period, \
      visit the <a href="https://facides.census.gov/Account/Login.aspx">Census Bureau</a>.';
    fyErrorContainer.appendChild(errorEl);
    fyFormGroup.classList.add('usa-form-group--error');
    fyErrorContainer.focus();
  } else {
    fyFormGroup.classList.remove('usa-form-group--error');
  }
}

/**
 * Wiring
 */
function attachValidateButtonHandler() {
  const btnValidate = document.getElementById('continue');

  btnValidate.addEventListener('click', (e) => {
    e.preventDefault();

    // guard (should already be disabled)
    if (!(requiredFieldsFilled() && FORM.checkValidity() && allResponsesValid())) return;

    duplicateReportIds = [];
    validateUEID();
  });
}

function wireFieldValidation() {
  const inputs = Array.from(document.querySelectorAll('#check-eligibility input'));

  inputs.forEach((el) => {
    el.addEventListener('blur', (e) => {
      if (validatorSupportsField(e.target)) {
        checkValidity(e.target);
      }
      updateValidateButtonState();
    });

    el.addEventListener('input', () => {
      duplicateReportIds = [];
      updateValidateButtonState();
    });

    el.addEventListener('change', (e) => {
      duplicateReportIds = [];

      if (e.target.id === 'auditee_fiscal_period_start') {
        validateFyStartDate(e.target);
      }

      if (validatorSupportsField(e.target)) {
        checkValidity(e.target);
      }

      updateValidateButtonState();
    });
  });
}


function init() {
  attachValidateButtonHandler();
  wireFieldValidation();
  updateValidateButtonState(); // initial disabled state
}

init();
