function init() {
  /*
    Grab form elements by [required] tag, and use them to enable/disable the submit button.
  */
  let d = document,
    [inputs, knapp] = [
      d.querySelectorAll('[required]'),
      d.querySelector('#continue'),
    ];
  knapp.disabled = true;

  for (var i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener('input', () => {
      let values = [];
      inputs.forEach((v) => values.push(v.value));
      knapp.disabled = values.includes('');
    });
  }
}

init();
