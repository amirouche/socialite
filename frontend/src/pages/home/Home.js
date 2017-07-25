import React from 'react';

import Shell from '../../components/shell/Shell.js';
import { Link, Title } from '../../forward.js';

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
        <Title title="Welcome to socialite" />
        <div id="login" className="box">
            <div id="login-input">
                <input type="text" placeholder="username" />
                <input type="password" placeholder="password" />
                <button>Submit</button>
            </div>
            <div id="login-extra">
                <p>
                    <Link mc={mc} href="/account/password-reset">Forgot your password</Link>
                </p>
                <p><Link mc={mc} href="/account/new">Create an account</Link></p>
            </div>
        </div>
    </Shell>
  );
}

export default Home;
