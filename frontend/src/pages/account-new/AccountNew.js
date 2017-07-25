import React from 'react';

import Shell from '../../components/shell/Shell.js';
import { Link, Title, saveAs, redirect } from '../../forward.js';

import './AccountNew.css';


var onClick = function(model) {
  return async function(event) {
    var response = await fetch('/api/status');
    console.log(response);
    return await redirect(model, '/');
  }
}


var AccountNew = function({model, mc}) {
  console.log(model.toJS());
  return (
    <Shell mc={mc}>
        <Title title="Create an account − socialite" />
        <div id="account-new" className="box">
            <h2>Create an account</h2>
            <div id="account-new-form">
                <input autoComplete="off"
                       type="text"
                       placeholder="username"
                       onChange={mc(saveAs('username'))}/>
                <input autoComplete="off"
                       type="password"
                       placeholder="password"
                       onChange={mc(saveAs('password'))} />
                <input type="password"
                       placeholder="password validation"
                       onChange={mc(saveAs('validation'))} />
                <button onClick={mc(onClick)}>Submit</button>
            </div>
        </div>
    </Shell>
  );
}

export default AccountNew;
