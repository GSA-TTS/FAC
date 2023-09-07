import { checkValidity } from './validate';

const FORM = document.forms[0];
const countrySelect = document.querySelector('#auditor_country');

function setFormDisabled(shouldDisable) {
  const continueBtn = document.getElementById('continue');
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
      if (input.id == 'audit-period-other') {
        monthsInput.removeAttribute('disabled');
      } else {
        monthsInput.setAttribute('disabled', true);
      }
    });
  });
  countrySelect.addEventListener('change', () => {
    setupAddress();
  });

  window.addEventListener('scroll', highlightActiveNavSection);
}
const foreignFields = document.querySelectorAll('[name="foreign_address"]');
const domesticFields = document.querySelectorAll('[name="domestic_address"]');
function setupAddress() {
  if (countrySelect.value == 'USA') {
    foreignFields.forEach((input) => {
      input.setAttribute('hidden', true);
      input.querySelectorAll('textarea').forEach((element) => {
        element.removeAttribute('required');
      });
    });
    domesticFields.forEach((input) => {
      input.removeAttribute('hidden');
      input.querySelectorAll('input').forEach((element) => {
        element.setAttribute('required', true);
      });
    });
  } else {
    foreignFields.forEach((input) => {
      input.removeAttribute('hidden');
      input.querySelectorAll('textarea').forEach((element) => {
        element.setAttribute('required', true);
      });
    });
    domesticFields.forEach((input) => {
      input.setAttribute('hidden', true);
      input.querySelectorAll('input').forEach((element) => {
        element.removeAttribute('required');
      });
    });
  }
}
function init() {
  attachEventHandlers();
  setupAddress();
}

init();
