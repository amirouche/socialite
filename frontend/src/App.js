import React from 'react';
import './App.css';

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

var App = function({model, mc}) {
  return (
    <div id="shell">
        <div id="menu">
            <ul>
                <li>Bookmarks</li>
                <li>Forum</li>
                <li>Messaging</li>
                <li>Search</li>
                <li>Wiki</li>                
            </ul>
        </div>
        <div id="header">
            <h1>Socialite</h1>
        </div>
        <div id="container">
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
        </div>
    </div>
  );
}

export default App;
