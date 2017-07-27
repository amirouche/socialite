import React from 'react';

import Shell from '../../components/shell/Shell.js';
import fw from '../../forward.js';
import api from '../../api.js';

import './AccountNew.css';


var onClick = function(model) {
  return async function(event) {
    var data = {
      username: model.get('username'),
      password: model.get('password'),
      validation: model.get('validation'),
      bio: model.get('bio', ''),
    };
    var response = await api.post('/api/account/new', data);
    if(response.ok) {
      return await fw.redirect(model, '/');
    } else if (response.status === 400) {
      var errors = await response.json();
      return (model) => model.set('errors', fw.fromJS(errors));
    }
  }
}


var AccountNew = function({model, mc}) {
  console.log(model.toJS());
  return (
    <Shell mc={mc}>
        <fw.Title title="Create an account − socialite" />
        <div id="account-new" className="box">
            <h2>Create an account</h2>
            <div id="account-new-form">
                <input type="text"
                       placeholder="username"
                       onChange={mc(fw.saveAs('username'))}/>
                <input type="password"
                       placeholder="password"
                       onChange={mc(fw.saveAs('password'))} />
                <input type="password"
                       placeholder="password validation"
                       onChange={mc(fw.saveAs('validation'))} />
                <textarea placeholder="bio"
                          onChange={mc(fw.saveAs('bio'))} />
                <button onClick={mc(onClick)}>Submit</button>
            </div>
        </div>
    </Shell>
  );
}

export default AccountNew;
