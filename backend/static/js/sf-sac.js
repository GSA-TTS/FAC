import { checkValidity } from './validate';

const FORM = document.forms[0];
const countrySelect = document.querySelector('#auditor_country');

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById('continue');

  if (!continueBtn) {
    return;
  }

  continueBtn.disabled = shouldDisable;
}

function allResponsesValid() {
  const inputsWithErrors = document.querySelectorAll('[class *="--error"]');
  return inputsWithErrors.length === 0;
}

function performValidations(field) {
  const inputType = field.type;
  if (inputType == 'radio') {
    const rgInputs = document.querySelectorAll(
      'input[name="' + field.name + '"]'
    );
    rgInputs.forEach((i) => i.classList.remove('usa-input--error'));
  }
  const errors = checkValidity(field);
  setFormDisabled(errors.length > 0);
}

// Fieldset elements with attribute "navitem" are watched. When scolled past, the applicable navLink is set to current.
function highlightActiveNavSection() {
  let currentFieldsetId;
  const fieldsets = document.querySelectorAll('fieldset[navitem]');
  const navLinks = document.querySelectorAll('li .usa-sidenav__item a');

  fieldsets.forEach((f) => {
    const fieldsetTop = f.offsetTop;
    if (scrollY >= fieldsetTop + 100) {
      currentFieldsetId = f.id;
    }
  });

  navLinks.forEach((l) => {
    if (currentFieldsetId) {
      l.classList.remove('usa-current');
    }

    if (l.getAttribute('href') == `#${currentFieldsetId}`) {
      l.classList.add('usa-current');
    }
  });
}

function attachEventHandlers() {
  // These fields no longer exist. The gen form is submittable in an incomplete state, so non-null data is okay.
  // Left alone for potential future enhancements on the form.
  const fieldsNeedingValidation = Array.from(
    document.querySelectorAll('.sf-sac input[data-validate-not-null]')
  );

  FORM.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!allResponsesValid()) return;
    FORM.submit();
  });

  fieldsNeedingValidation.forEach((q) => {
    q.addEventListener('blur', (e) => {
      performValidations(e.target);
    });
  });

  const rbInputs = document.querySelectorAll('[name="audit_period_covered"]');
  const monthsInput = document.querySelector('#audit_period_other_months');
  rbInputs.forEach((input) => {
    input.addEventListener('change', () => {
      if (!monthsInput) {
        return;
      }

      if (input.id === 'audit-period-other') {
        monthsInput.removeAttribute('disabled');
      } else {
        monthsInput.setAttribute('disabled', true);
      }
    });
  });
  if (countrySelect) {
    countrySelect.addEventListener('change', setupAddress);
  }

  window.addEventListener('scroll', highlightActiveNavSection);
}

const foreignFields = document.querySelectorAll('[name="foreign_address"]');
const domesticFields = document.querySelectorAll('[name="domestic_address"]');
function setupAddress() {
  if (!countrySelect) {
    return;
  }

  if (countrySelect.value === 'USA') {
    foreignFields.forEach((input) => {
      input.setAttribute('hidden', true);
    });

    domesticFields.forEach((input) => {
      input.removeAttribute('hidden');
    });
  } else {
    foreignFields.forEach((input) => {
      input.removeAttribute('hidden');
    });

    domesticFields.forEach((input) => {
      input.setAttribute('hidden', true);
    });
  }
}

function setupAuditeeEinWarning() {
  const auditeeEinInput = document.getElementById('ein');
  const auditeeEinWarning = document.getElementById(
    'auditee-ein-warning'
  );
  const auditeeEinWarningText = document.getElementById(
    'auditee-ein-warning-text'
  );

  if (
    !auditeeEinInput ||
    !auditeeEinWarning ||
    !auditeeEinWarningText
  ) {
    return;
  }

  let timer;
  let abortController;

  const hideWarning = () => {
    auditeeEinWarning.hidden = true;
    auditeeEinWarningText.textContent = '';
  };

  const checkEin = async () => {
    const currentEin = auditeeEinInput.value.trim();
    const warningUrl = auditeeEinInput.dataset.warningUrl;

    // Remove any dashes or other non-numeric characters
    const normalizedEin = currentEin.replace(/\D/g, '');

    // Only check once a full 9-digit EIN has been entered
    if (normalizedEin.length !== 9 || !warningUrl) {
      hideWarning();
      return;
    }

    if (abortController) {
      abortController.abort();
    }

    abortController = new AbortController();

    const url = new URL(warningUrl, window.location.origin);
    url.searchParams.set('ein', normalizedEin);

    try {
      const response = await fetch(url, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(
          `EIN warning request failed: ${response.status}`
        );
      }

      const data = await response.json();

      if (data.warning) {
        auditeeEinWarningText.textContent = data.warning;
        auditeeEinWarning.hidden = false;
      } else {
        hideWarning();
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error(error);
        hideWarning();
      }
    }
  };

  auditeeEinInput.addEventListener('input', () => {
    window.clearTimeout(timer);
    timer = window.setTimeout(checkEin, 400);
  });
}

function init() {
  setupAuditeeEinWarning();

  if (FORM) {
    attachEventHandlers();
  }

  if (countrySelect) {
    setupAddress();
  }
}

init();
