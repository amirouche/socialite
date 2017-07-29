import React from 'react';

import Shell from '../../components/shell/Shell.js';
import fw from '../../forward.js';

import './Home.css';

/*
 * var test = async function() {
 *   var response = await fetch('/api/status');
 *   var body = await response.json();
 *   return body;
 * }
 *
 * test().then(function(body) { console.log(arguments); });
 * */

/*
 * var Child = function({children, model, mc}) {
 *   return <div>{children}</div>
 * }
 * */

var Home = function({model, mc}) {
  return (
    <Shell mc={mc}>
        <fw.Title title="Welcome to socialite" />
        <div id="login" className="box">
            <div id="login-input">
                <input type="text" placeholder="username" />
                <input type="password" placeholder="password" />
                <button>Submit</button>
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
