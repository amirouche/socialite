import React from 'react';
import { Input, Button } from 'reactstrap';

import fw from '../../forward.js';
import Shell from '../../components/shell/Shell.js';

import './wiki_edit.css';


let page_not_found_message = function(title) {
  return `## ${title}

Let's get started with a new page. You can use commonmark flavor of markdown.`
}


let init = async function(model) {
  let response = await fw.post('/api/check_auth', {}, fw.getToken(model))
  if (response.ok) {
    let title = model.getIn(['%location', 'params', 'title']);
    let url = `/api/wiki/${title}/latest`;
    response = await fw.get(url, fw.getToken(model));
    if(response.ok) {
      let page = await response.json();
      console.log(page);
      return model => model.set('body', page.body).set('title', title);
    } else {
      return model => model.set('body', page_not_found_message(title)).set('title', title);
    }
  } else {
    return fw.redirect(model, '/');
  }
}

let onClick = function(model) {
  return async function(event) {
    let title = model.get('title');
    let body = model.get('body');
    let url = `/api/wiki/${title}/edit`;
    var response = await fw.post(url, {body: body}, fw.getToken(model));
    if (response.ok) {
      return await fw.redirect(model, `/wiki/${title}`);
    } else {
      // FIXME: handle error
      return model => model;
    }
  }
}

let WikiEdit = function({mc, model}) {
  let body = model.get('body');
  let title = model.get('title');

  return (
    <Shell>
      <h1>Socialite wiki</h1>
      <div id="wiki-edit">
        <h2>Edit {title}</h2>
        <Input type="textarea" onChange={mc(fw.saveAs('body'))} value={body} />
        <Button onClick={mc(onClick)}>Submit</Button>
      </div>
    </Shell>
  )
}

export default {
  init,
  WikiEdit,
}
