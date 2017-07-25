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
        <div id="login">
            <div id="login-input">
                <input type="text" placeholder="login" />
                <input type="password" placeholder="password" />
                <button>Submit</button>
            </div>
            <div id="login-extra">
                <p><a href="/">Forgot your password</a></p>
                <p><a href="/">Create an account</a></p>
            </div>
        </div>
    </Shell>
  );
}

export default Home;
