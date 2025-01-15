var FORM = document.getElementById('audit-search-form');
const pagination_links = document.querySelectorAll('[aria-label^="Page"]');
const next_page_link = document.querySelectorAll('[aria-label="Next page"]');
const search_submit_buttons = document.querySelectorAll('[type="submit"]');
const previous_page_link = document.querySelectorAll(
  '[aria-label="Previous page"]'
);
const loader = document.getElementById(`loader`);
const search_arrow = document.getElementById(`search_arrow`);

/**
 * Attach event handlers for the pagination buttons. On click, set the appropriate form inputs and submit it for a reload.
 */
function attachEventHandlersPagination() {
  pagination_links.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      FORM.elements['page'].value = link.textContent;
      FORM.submit();
    });
  });

  if (next_page_link[0]) {
    next_page_link[0].addEventListener('click', (e) => {
      e.preventDefault();
      FORM.elements['page'].value = parseInt(FORM.elements['page'].value) + 1;
      FORM.submit();
    });
  }
  if (previous_page_link[0]) {
    previous_page_link[0].addEventListener('click', (e) => {
      e.preventDefault();
      FORM.elements['page'].value = parseInt(FORM.elements['page'].value) - 1;
      FORM.submit();
    });
  }
}

/**
 * Attach an event listener to form 'reset' event.
 * On form reset, wipe all fields and return them to their default states.
 */
function attachEventHandlersReset() {
  // The standard form behavior does _not_ reset to fully empty fields if the user had just made a search.
  FORM.addEventListener('reset', (e) => {
    e.preventDefault();

    resetCheckboxes();
    resetCogOver();

    // Empty out textareas
    var text_areas = document.getElementsByTagName('textarea');
    Array.from(text_areas).forEach((input) => {
      input.value = '';
    });
    // Wipe date fields
    var date_inputs = document.querySelectorAll(
      'div.usa-date-picker__wrapper > input'
    );
    Array.from(date_inputs).forEach((date_input) => {
      date_input.value = '';
    });
    // Reset state dropdown
    var default_state_option = document.getElementById('state--none');
    default_state_option.selected = true;
    // Reset fiscal year end month
    var default_FY_option = document.getElementById('fy-month--none');
    default_FY_option.selected = true;

    FORM.reset();
  });
}

/**
 * Reset the checkboxes. Clears audit year, entity type, etc.
 * Re-check audit year 2023.
 */
function resetCheckboxes() {
  var all_checkboxes = document.querySelectorAll(
    '[type="checkbox"], [type="radio"]'
  );
  var AY_checkboxes = document.querySelectorAll('input[id^=audit-year]');

  Array.from(all_checkboxes).forEach((checkbox) => {
    checkbox.checked = false;
  });
  if (AY_checkboxes[1]) {
    AY_checkboxes[1].checked = true;
  }
}

/**
 * Reset the Cognizant or Oversight fields, if they exist.
 */
function resetCogOver() {
  var default_cog_over_option = document.getElementById(
    'cog_or_oversight--either'
  );
  var cog_over_agency_number = document.getElementById('agency-name');
  if (default_cog_over_option) {
    default_cog_over_option.selected = true;
    cog_over_agency_number.value = '';
  }
}

/**
 * Attach event handlers to the sort buttons in the table header.
 * When clicked, set the appropriate sort direction in the form inputs and submit for a reload.
 */
function attachEventHandlersSorting() {
  /*
    Get the table headers and their sort buttons.
    Using the ID of the table headers, attach event handlers to re-submit the form when clicking them.
    This will reload the page with the associated sort values, so that searches appear to sort across many pages.

    If the sort buttons get clicked, we have one of three states:
      1. We are not sorting, and we move to sort in descending.
      2. We are sorting by descending, and we move to sort in ascending.
      3. We are sorting by ascending, and we move to no sort at all.
        i. In this case, we wipe both the order_by and order_direction fields. Or, it will maintain the values and sort anyway.
    In any case, we want to reset the page number to one.
  */
  var FORM = document.getElementById('audit-search-form');
  var table_headers = document.querySelectorAll('th[id]');

  table_headers.forEach((header) => {
    var button = header.querySelector('button');
    var current_sort = header.getAttribute('aria-sort');

    button.addEventListener('click', (e) => {
      e.preventDefault();

      if (current_sort == 'ascending') {
        FORM.elements['order_direction'].value = '';
        FORM.elements['order_by'].value = '';
      } else if (current_sort == 'descending') {
        FORM.elements['order_by'].value = header.id;
        FORM.elements['order_direction'].value = 'ascending';
      } else {
        FORM.elements['order_by'].value = header.id;
        FORM.elements['order_direction'].value = 'descending';
      }
      FORM.elements['page'].value = 1;

      FORM.submit();
    });
  });
}

/**
 * Attach event listeners for form submission.
 * On clicking "Search", disable both search buttons and show the loader instead of the arrow image, then submit.
 */
function attachEventHandlersSubmission() {
  search_submit_buttons.forEach((button) => {

    // The first search button is always for searching all of fac.gov, we want to ignore that one hence skipping.
    if (button.id  === 'fac-search') return;

    button.addEventListener('click', () => {
      // The arrow won't be there if results were previously populated
      if (search_arrow) {
        search_arrow.hidden = true;
      }

      loader.hidden = false;

      search_submit_buttons.forEach((btn) => {
        btn.disabled = true;
        btn.value = 'Searching...';
      });

      FORM.submit();
    });
  });
}

function init() {
  attachEventHandlersPagination();
  attachEventHandlersReset();
  attachEventHandlersSorting();
  attachEventHandlersSubmission();
}

window.onload = init;
