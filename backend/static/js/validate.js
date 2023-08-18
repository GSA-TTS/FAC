export const checkValidity = (field) => {
  const errors = [];
  const checks = parseChecks(field);
  const identifier = field.type == 'radio' ? field.name : field.id;

  for (const [operation, constraint] of Object.entries(checks)) {
    const result = validations[operation](field, constraint);

    if (result.error) {
      toggleErrorClass(field, true);
      toggleErrorMessageContainer(identifier, true, field);
      toggleErrorMessages(identifier, result, true);
      toggleAriaDescribedBy(field, identifier, true);
      errors.push(validations[operation](field, constraint));
    } else {
      toggleErrorMessages(identifier, result, result.error);
      toggleAriaDescribedBy(field, identifier, false);
    }
  }

  if (errors.length == 0) {
    toggleErrorClass(field, false);
    toggleErrorMessages(identifier, null, false);
    toggleErrorMessageContainer(identifier, false);
  }

  return errors;
};

const toggleErrorMessageContainer = (id, shouldDisplay) => {
  const errorContainer = document.getElementById(`${id}-error-message`);
  const parent = errorContainer.parentElement;
  toggleErrorClass(parent, shouldDisplay, 'usa-form-group--error');
};

const toggleErrorMessages = (id, error, isInvalid) => {
  if (error) {
    const errorMessage = document.getElementById(`${id}-${error.validation}`);
    errorMessage.hidden = !isInvalid;
  }
};

const toggleErrorClass = (field, isInvalid, errorClass) => {
  const klass = errorClass ? errorClass : 'usa-input--error';

  isInvalid ? field.classList.add(klass) : field.classList.remove(klass);
};

const toggleAriaDescribedBy = (field, id, isInvalid) => {
  if (isInvalid) {
    field.setAttribute('aria-describedby', `${id}-error-message`);
  } else {
    field.removeAttribute('aria-describedby');
  }
};

const filterObjectByKey = (objToFilter, condition) => {
  const filteredObj = {};
  const keys = Object.keys(objToFilter).filter(condition);
  keys.forEach((k) => {
    filteredObj[k] = objToFilter[k];
  });
  return filteredObj;
};

export const parseChecks = (field) => {
  const containsValidate = (str) => str.match('validate');
  const validations = filterObjectByKey(field.dataset, containsValidate);

  return validations;
};

const radioChecked = (name) => {
  const checked = document.querySelector(`[name="${name}"]:checked`);
  return !!checked;
};

export const validations = {
  validateEmail: (field) => {
    const result = {
      error: false,
      fieldId: field.id,
      validation: 'email',
    };

    const minimal_email_regex = /.+@.+\..+/;
    return field.value && !minimal_email_regex.test(field.value)
      ? { ...result, error: true }
      : result;
  },

  validateNotNull: (field) => {
    const result = {
      error: false,
      fieldId: field.id,
      validation: 'not-null',
    };

    if (field.type == 'checkbox') {
      return !field.checked ? { ...result, error: true } : result;
    }

    switch (field.type) {
      case 'text':
      case 'search':
        return !field.value ? { ...result, error: true } : result;
      case 'radio':
        return !radioChecked(field.name) ? { ...result, error: true } : result;
      case 'checkbox':
        return !field.checked ? { ...result, error: true } : result;
      case 'select-one':
        return !field.value != '' ? { ...result, error: true } : result;
    }

    return !field.value || !field.checked ? { ...result, error: true } : result;
  },

  validateMatchedField: (field, matchField) => {
    const matchFieldEl = document.querySelector(`input#${matchField}`);
    const result = {
      error: false,
      fieldId: field.id,
      validation: 'matched-field',
    };
    const isMatchedForgotten = field.value && !matchFieldEl.value;
    return isMatchedForgotten
      ? { ...result, error: true }
      : result;
  },

  validateMustMatch: (field, matchField) => {
    const matchFieldEl = document.querySelector(`input#${matchField}`);
    const result = {
      error: false,
      fieldId: field.id,
      validation: 'must-match',
    };

    return field.value != matchFieldEl.value
      ? { ...result, error: true }
      : result;
  },

  validateLength: (field, compStr) => {
    const [comparator, compValue] = compStr.split(' ');
    const valueLength = field.value.length;
    const compValueLength = parseInt(compValue);

    const result = {
      error: false,
      fieldId: field.id,
      validation: 'length',
    };

    switch (comparator) {
      case '==':
        return valueLength != compValueLength
          ? { ...result, error: true }
          : result;
    }
  },
};
