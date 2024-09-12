/**
 * Attach an event handler to every button with attribute "disable-submit-after-click".
 * This will disable the button after clicking it, enable the sibling spinning icon
 * (if it exists), and submit the form.
 */
function disableSubmitAfterClick() {
  const matching_buttons = document.querySelectorAll(
    'button[disable-submit-after-click]'
  );

  matching_buttons.forEach((button) => {
    const form = button.closest('form'); // Parent form
    const loader = button.parentElement.querySelector(`div[id='loader']`); // Sibling loader

    button.addEventListener('click', () => {
      button.disabled = true;
      button.textContent = 'Submitting...';
      if (loader) {
        loader.hidden = false;
      }
      form.submit();
    });
  });
}

function init() {
  disableSubmitAfterClick();
}

window.onload = init;
