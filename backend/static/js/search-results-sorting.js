function attachEventHandlers() {
  var FORM = document.getElementById('search-form');
  var table_headers = document.querySelectorAll('th[id]');

  table_headers.forEach((header) => {
    var button = header.querySelector("button");
    var current_sort = header.getAttribute('aria-sort')

    button.addEventListener('click', (e) => {
      e.preventDefault();

      if (current_sort == "ascending"){
        FORM.elements['sort_by'].value = `-${header.id}`;
      } else if (current_sort == "descending") {
        FORM.elements['sort_by'].value = "";
      } else {
        FORM.elements['sort_by'].value = header.id;
      }

      FORM.submit();
    });
  });

}

function init() {
  attachEventHandlersPagination();
  attachEventHandlersSorting();
}

window.onload = init;
