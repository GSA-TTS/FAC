export const getCookie = () => {
  const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (csrfInput !== null) {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
  return null;
};
