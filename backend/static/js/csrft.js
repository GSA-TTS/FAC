export const getCookie = () => {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
};
