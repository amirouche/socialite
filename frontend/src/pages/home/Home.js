import React from 'react';

import Shell from '../../components/shell/Shell.js';
import fw from '../../forward.js';

import './Home.css';


var onSubmit = function(app, model) {
    return async function(event) {
        var data = {
            username: model.get('username'),
            password: model.get('password'),
        }
        var response = await fw.post('/api/account/login', data);
        if (response.ok) {
            var json = await response.json();
            var token = json.token;
            // Save the token inside localStorage for future use,
            // it replace the use of a cookie
            window.localStorage.setItem('%token', token)
            // goto the dashboard now
            return await fw.redirect(app, model, '/dashboard');
        } else {
            console.log('login failed', model.toJS());
        }
    }
}


var Home = function(model, mc) {
    fw.log('Home', model.toJS());
    return (
        <Shell mc={mc}>
            <fw.Title title="Welcome to socialite" />
            <div id="login" className="box">
                <div id="login-input">
                    <h1>Socialite</h1>
                    <fw.Input type="text"
                              label="username"
                              onChange={mc(fw.set('username'))} />
                    <fw.Input type="password"
                              label="password"
                              onChange={mc(fw.set('password'))} />
                    <fw.Button onClick={mc(onSubmit)}>Submit</fw.Button>
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
