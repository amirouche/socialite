var get = function(path, token) {
  var request = new Request(path);
  if (token) {
    request.headers.set('X-AUTH-TOKEN', token)
  }
  return fetch(request);
}

var post = function(path, data, token) {
  var request = new Request(path, {method: 'POST', body: JSON.stringify(data)});
  if (token) {
    request.headers.set('X-AUTH-TOKEN', token);
  }
  return fetch(request);
}

export default {
  get,
  post
}
