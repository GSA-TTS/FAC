export const getCookie = (name) => {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
};
