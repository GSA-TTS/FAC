var FORM = document.getElementById('search-form');
const pagination_links = document.querySelectorAll('[aria-label^="Page"]');
const next_page_link = document.querySelectorAll('[aria-label="Next page"]');
const previous_page_link = document.querySelectorAll(
  '[aria-label="Previous page"]'
);

function attachEventHandlers() {
  // If any pagination links are clicked, set the form element and submit it for a reload
  pagination_links.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      FORM.elements['page'].value = link.textContent;
      FORM.submit();
    });
  });
  // If the next or previous page buttons are clicked, set the form element to be +/- 1 and submit for a reload
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

function init() {
  attachEventHandlers();
}

window.onload = init;
