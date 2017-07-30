import React from 'react';
import fw from '../../forward.js';
import Shell from '../../components/shell/Shell.js';


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
          <p>Let's discuss together in live</p>
        </fw.Link>
      </div>
    </Shell>
  )
}

export default {
  init: init,
  Dashboard: Dashboard,
}
