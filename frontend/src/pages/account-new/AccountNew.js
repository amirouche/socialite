import React from 'react';

import Shell from '../../components/shell/Shell.js';
import fw from '../../forward.js';

import './AccountNew.css';


var onClick = function(model) {
  return async function(event) {
    var data = {
      username: model.get('username'),
      password: model.get('password'),
      validation: model.get('validation'),
      bio: model.get('bio', ''),
    };
    var response = await fw.post('/api/account/new', data);
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
                <fw.Input type="text"
                          label="username"
                          text="It must be neat!"
                          error={model.getIn(['errors', 'username'])}
                          onChange={mc(fw.saveAs('username'))} />
                <fw.Input type="password"
                          label="password"
                          text="It must strong."
                          error={model.getIn(['errors', 'password'])}
                          onChange={mc(fw.saveAs('password'))} />
                <fw.Input type="password"
                          label="validation"
                          text="Re-type your password to be sure."
                          error={model.getIn(['errors', 'validation'])}
                          onChange={mc(fw.saveAs('validation'))} />
                <fw.Input type="textarea"
                          label="bio"
                          text="Filler text..."
                          error={model.getIn(['errors', 'bio'])}
                          onChange={mc(fw.saveAs('bio'))} />
                <button onClick={mc(onClick)}>Submit</button>
            </div>
        </div>
    </Shell>
  );
}

export default AccountNew;
