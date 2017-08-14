import React from 'react';
import ReactMarkdown from 'react-markdown';

import fw from '../../forward.js';
import Shell from '../../components/shell/Shell.js';

import './wiki.css';


let page_not_found_message = function(title) {
  return `## Page not found

The page you requested was not found on this server.

You can [create it](/wiki/${title}/edit).`
}

let init = async function(model) {
  let response = await fw.post('/api/check_auth', {}, fw.getToken(model))
  if (response.ok) {
    let title = model.getIn(['%location', 'params', 'title']);
    let url = `/api/wiki/${title}/latest`;
    response = await fw.get(url, fw.getToken(model));
    if(response.ok) {
      let page = await response.json();
      page = fw.fromJS(page);
      page = page.set('title', title);
      return model => model.set('page', page);
    } else {
      let page = {
        body: page_not_found_message(title),
        title: title,
      };
      return model => model.set('page', fw.fromJS(page));
    }
  } else {
    return fw.redirect(model, '/');
  }
}

let Wiki = function({mc, model}) {
  let body = model.getIn(['page', 'body']);
  return (
    <Shell>
      <h1>Socialite wiki</h1>
      <div id="wiki">
        <ReactMarkdown source={body} />
      </div>
    </Shell>
  )
}

export default {
  init,
  Wiki,
}
