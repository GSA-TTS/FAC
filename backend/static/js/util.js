/**
 * Attach an event handler to every button with attribute "disable-submit-after-click".
 * This will disable the button after clicking it, and submit the form.
 * This is intended to prevent duplicate form submissions where it would be very inconvenient.
 */
function disableSubmitAfterClick() {
  const matching_buttons = document.querySelectorAll(
    'button[disable-submit-after-click]'
  );

  matching_buttons.forEach((button) => {
    var form = button.closest('form');

    button.addEventListener('click', () => {
      button.disabled = true;
      button.value = 'Submitting...';
      form.submit()
    });
  });
}

function init() {
  disableSubmitAfterClick();
}

window.onload = init;
