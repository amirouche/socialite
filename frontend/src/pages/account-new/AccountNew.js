import React from 'react';

import Shell from '../../components/shell/Shell.js';
import { Link, Title, saveAs } from '../../forward.js';

import './AccountNew.css';


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
                <button>Submit</button>
            </div>
        </div>
    </Shell>
  );
}

export default AccountNew;
