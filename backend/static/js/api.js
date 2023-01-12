export const queryAPI = (
  endpoint,
  data,
  config,
  [handleResponse, handleError]
) => {
  const headers = new Headers();
  headers.append('Content-type', 'application/json');
  fetch(endpoint, {
    method: config.method,
    headers: headers,
    body: JSON.stringify(data),
  })
    .then((resp) => resp.json())
    .then((data) => handleResponse(data))
    .catch((e) => handleError(e));
}; 