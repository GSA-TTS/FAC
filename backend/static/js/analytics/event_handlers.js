/**
 * Event handlers for the analytics pages.
 */

var FORM = document.getElementById('analytics-filter-form');

/**
 * Attach an event listener to form 'reset' event.
 * On form reset, wipe all fields and return them to their default states.
 * The standard form behavior does _not_ reset to fully empty fields if the user had just set a filter.
 */
function attachEventHandlersReset() {
  FORM.addEventListener('reset', (e) => {
    e.preventDefault();

    // Reset Checkboxes
    var all_checkboxes = document.querySelectorAll(
      '[type="checkbox"]'
    );
    Array.from(all_checkboxes).forEach((checkbox) => {
      checkbox.checked = false;
    });

    // Reset state dropdown
    var default_state_option = document.getElementById('state--none');
    default_state_option.selected = true;

    FORM.reset();
  });
}

function init() {
  attachEventHandlersReset();
}

window.onload = init;
