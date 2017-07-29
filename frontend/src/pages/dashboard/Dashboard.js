import React from 'react';
import fw from '../../forward.js';


var Dashboard = function({mc, model}) {
  return (
    <div>
        <h1>Welcome to Socialite</h1>
    </div>
  )
}

export default {
  init: fw.clean,
  Dashboard: Dashboard,
}
