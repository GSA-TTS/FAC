var FORM = document.getElementById('search-form');
const pagination_links = document.querySelectorAll('[aria-label^="Page"]');
const next_page_link = document.querySelectorAll('[aria-label="Next page"]');
const previous_page_link = document.querySelectorAll(
  '[aria-label="Previous page"]'
);

/*
  If any pagination links are clicked, set the page form element and submit it for a reload.
  If the next or previous page buttons are clicked, set the page form element to be +/- 1 and submit for a reload.
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

/*
  The standard form behavior resets to the default value, which is whatever the user entered on the last form submission, _not_ fully empty fields.
  We cannot just loop over every form element, because buttons and hidden inputs should be handled differently.
*/
function attachEventHandlersReset() {
  FORM.addEventListener('reset', (e) => {
    e.preventDefault();
    // Empty out textareas
    var text_areas = document.getElementsByTagName('textarea');
    Array.from(text_areas).forEach((input) => {
      input.value = '';
    });
    // Uncheck checkboxes
    var checkboxes = document.querySelectorAll(
      '[type="checkbox"], [type="radio"]'
    );
    Array.from(checkboxes).forEach((checkbox) => {
      checkbox.checked = false;
    });
    // Wipe FAC release dates
    var start_date = document.getElementById('start-date');
    var end_date = document.getElementById('end-date');
    start_date.value = '';
    end_date.value = '';
    // Reset Cog/Over dropdown
    var default_cog_over_option = document.getElementById(
      'cog_or_oversight--none'
    );
    default_cog_over_option.selected = true;
    // Wipe agency name
    var agency_name = document.getElementById('agency-name');
    agency_name.value = '';
    // Reset state dropdown
    var default_state_option = document.getElementById('state--none');
    default_state_option.selected = true;

    FORM.reset();
  });
}

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
function attachEventHandlersSorting() {
  var FORM = document.getElementById('search-form');
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

function init() {
  attachEventHandlersPagination();
  attachEventHandlersReset();
  attachEventHandlersSorting();
}

window.onload = init;
