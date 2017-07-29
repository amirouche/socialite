import React from 'react';

import Shell from '../../components/shell/Shell.js';
import fw from '../../forward.js';

import './Home.css';


var onSubmit = function(model) {
  return async function(event) {
    var data = {
      username: model.get('username'),
      password: model.get('password'),
    }
    var response = await fw.post('/api/account/login', data);
    if (response.ok) {
      var json = await response.json();
      var token = json.token;
      var newModel = model.set('%token', token);
      return await fw.redirect(newModel, '/dashboard');
    } else {
      console.log('login failed', model.toJS());
    }
  }
}


var Home = function({model, mc}) {
  console.log('Home', model.toJS());
  return (
    <Shell mc={mc}>
        <fw.Title title="Welcome to socialite" />
        <div id="login" className="box">
            <div id="login-input">
                <h1>Socialite</h1>
                <fw.Input type="text"
                          label="username"
                          onChange={mc(fw.saveAs('username'))} />
                <fw.Input type="password"
                          label="password"
                          onChange={mc(fw.saveAs('password'))} />
                <button onClick={mc(onSubmit)}>Submit</button>
            </div>
            <div id="login-extra">
                <p>
                    <fw.Link mc={mc} href="/account/password-reset">Forgot your password</fw.Link>
                </p>
                <p><fw.Link mc={mc} href="/account/new">Create an account</fw.Link></p>
            </div>
        </div>
    </Shell>
  );
}

export default Home;
