import React from 'react';
import './index.css';
import registerServiceWorker from './registerServiceWorker';
import ff from './ff.js';


let Home = function(model) {
    return [
        <div id="header" key="header">
            <input type="text" placeholder="incoming!" />
            <button><span role="img" aria-label="submit">🚀</span></button>
        </div>,
        <div id="container" key="container">
            <div className="directory">
                <p className="name">Programming</p>
                <p className="updates">linux.org, hackernews, journal du hacker</p>
                <p className="toolbox"><span rol="img">✓</span></p>
            </div>
            <div className="directory open">
                <h2 className="name">Programming</h2>
                <ul>
                    <li>ff.js yet another javascript framework (github.com)</li>
                    <li>aiohttp the win-win python framework (python.org)</li>
                    <li className="open">
                        <div>
                            <h3>incoming feed reader from space <small>(hyperdev.fr)</small></h3>
                            <p>lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet</p>
                        </div>
                    </li>
                    <li>scheme todomvc app (github.com)</li>
                </ul>
            </div>
            <div className="directory">
                <p className="name">Programming</p>
                <p className="updates">linux.org, hackernews, journal du hacker</p>
                <p className="toolbox"><span rol="img">✓</span></p>
            </div>
            <div className="directory">
                <p className="name">Programming</p>
                <p className="updates">linux.org, hackernews, journal du hacker</p>
                <p className="toolbox"><span rol="img">✓</span></p>
            </div>
        </div>
    ];
}


let onSignIn = function(app, model) {
    return async function(event) {
        event.preventDefault();
        return (app, model) => model;
    }
}

let onSignUp = function(app, model) {
    return async function(event) {
        event.preventDefault();
        let data = {
            username: model['signup-username'],
            password: model['signup-password'],
            validation: model['signup-validation']
        };
        let response = await ff.post('/api/account/new', data);
        if(response.status === 400) {
            let error = await response.json();
            Object.keys(error).forEach(function(key) {
                error['signin-' + key] = error[key];
                delete error[key];
            });
            return (app, model) => model.set('error', ff.Immutable(error))
                                        .set('kind', 'signup');
        }
        if(response.status === 200) {
            return await ff.redirect(app, model, '/');
        }
        return (app, model) => model.set('error', {form: 'An error occured'});
    }
}


let getErrorMessage = function(name, model) {
    if (model.getIn(['error', name])) {
        return <p className="error">{model['error'][name]}</p>;
    } else {
        return '';
    }
}

let Index = function(model, mc) {
    ff.log('model', model);
    return (
        <div id="container">
            <div id="enter">
                <h2>Sign In</h2>
                <form onSubmit={mc(onSignIn)}>
                    <p><input type="text"
                              placeholder="username"
                              value={model['signin-username'] || ""}
                              onChange={mc(ff.set('signin-username'))}/></p>
                    {getErrorMessage('sigin-username', model)}
                    <p><input type="password"
                              placeholder="password"
                              value={model['signin-password'] || ""}
                              onChange={mc(ff.set('sigin-password'))}/></p>
                    {getErrorMessage('sigin-password', model)}
                    <p><input type="submit" value="submit" onClick={mc(onSignIn)}/></p>
                    {getErrorMessage('sigin-form', model)}
                </form>
                <h2>Sign Up</h2>
                <form onSubmit={mc(onSignUp)}>
                    <p><input type="text"
                              placeholder="username"
                              value={model['signup-username'] || ""}
                              onChange={mc(ff.set('signup-username'))}/></p>
                    {getErrorMessage('signup-username', model)}
                    <p><input type="password"
                              placeholder="password"
                              value={model['signup-password'] || ""}
                              onChange={mc(ff.set('signup-password'))}/></p>
                    {getErrorMessage('signup-password', model)}
                    <p><input type="password"
                              placeholder="validation"
                              value={model['signup-validation'] || ""}
                              onChange={mc(ff.set('signup-validation'))}/></p>
                    {getErrorMessage('signup-validation', model)}
                    <p><input type="submit" value="submit" onSubmit={mc(onSignUp)}/></p>
                    {getErrorMessage('signup-form', model)}
                </form>
            </div>
        </div>
    );
}



let router = new ff.Router();
router.append('/', ff.clean, Index);
router.append('/home', ff.clean, Home);




ff.createApp(router);

registerServiceWorker();
