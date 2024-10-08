import { getCookie } from './csrft';
const csrftoken = getCookie('csrftoken');

export const queryAPI = (
  endpoint,
  data,
  config,
  [handleResponse, handleError]
) => {
  const headers = new Headers();
  headers.append('Content-type', 'application/json');
  headers.append('X-CSRFToken', csrftoken);
  fetch(endpoint, {
    method: config.method,
    headers: headers,
    body: JSON.stringify(data),
  })
    .then((resp) => resp.json())
    .then((data) => handleResponse(data))
    .catch((e) => handleError(e));
};
