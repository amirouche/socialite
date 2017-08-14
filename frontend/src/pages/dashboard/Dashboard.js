import React from 'react';
import fw from '../../forward.js';
import Shell from '../../components/shell/Shell.js';

import './dashboard.css';


var init = async function(model) {
  var response = await fw.post('/api/check_auth', {}, fw.getToken(model))
  if (!response.ok) {
    return fw.redirect(model, '/');
  } else {
    return (model) => model;
  }
}

var Dashboard = function({mc, model}) {
  return (
    <Shell>
      <h1>Welcome to Socialite</h1>
      <div id="dashboard">
        <fw.Link mc={mc} href="/chat" className="box">
          <h2>Chat</h2>
          <p>Discuss live important and less important matters</p>
        </fw.Link>
        <fw.Link mc={mc} href="/wiki" className="box">
          <h2>Wiki</h2>
          <p>Collaboratively modify content and structure it directly from the web browser.</p>
        </fw.Link>
      </div>
    </Shell>
  )
}

export default {
  init: init,
  Dashboard: Dashboard,
}
