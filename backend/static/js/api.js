//import { getApiToken } from '/static/compiled/js/auth.js';

export const queryAPI = (
  endpoint,
  data,
  config,
  [handleResponse, handleError]
) => {
  const apiUrl = 'https://fac-dev.app.cloud.gov';
  const headers = new Headers();

  headers.append('Content-type', 'application/json');

  getApiToken().then((token) => {
    headers.append('Authorization', 'Token ' + token); // authToken is set in a script tag right before this script loads

    fetch(apiUrl + endpoint, {
      method: config.method,
      headers: headers,
      body: JSON.stringify(data),
    })
      .then((resp) => resp.json())
      .then((data) => handleResponse(data))
      .catch((e) => handleError(e));
  });
};
