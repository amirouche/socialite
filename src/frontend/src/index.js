import React from 'react';
import './index.css';
import registerServiceWorker from './registerServiceWorker';
import ff from './ff.js';


let check = async function(app, model) {
    model = (await ff.clean(model));
    let token = ff.getToken(model);
    if (token !== undefined) {
        let response = await ff.post('/api/check_auth', {}, ff.getToken(model));
        if (response.status === 200) {
            let response = await ff.post('/api/home', '', ff.getToken(model));
            let output = await response.json();
            return (app, _) => model.set('output', output);
        } else {
            return await ff.redirect(app, model, '/');
        }
    } else {
        return await ff.redirect(app, model, '/');
    }
}

let onSubmit = function(app, model) {
    return async function(event) {
        event.preventDefault();
        let response = await ff.post('/api/home', model['input'], ff.getToken(model));
        let out = await response.json();
        return (app, model) => model.set('kind', out['kind'])
                                    .set('output', out['output']);
    }
}


let defaultHome = function(model, mc) {
    return (
        <div id="container" key="container">
            <div className="directory">
                <p className="name">Programming</p>
                <p className="updates">linux.org, hackernews, journal du hacker</p>
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
            </div>
            <div className="directory">
                <p className="name">Programming</p>
                <p className="updates">linux.org, hackernews, journal du hacker</p>
            </div>
        </div>
    );
}

let feedViewEntry = function(entry) {
    return <li key={entry['link']}><a href={entry['link']} target="_blank">{entry['title']}</a></li>;
}

let feedView = function(output, mc) {
    let key = 'feed-' + output['title'];
    return (
        <div id="container" key={key}>
            <div className="info">
                <p>Use <code>/add FEED CATEGORY</code> to add <code>FEED</code> to <code>CATEGORY</code></p>
            </div>
            <div className="directory open">
                <h2 className="name">{output['title']}</h2>
                <ul>
                    {output['entries'].map(feedViewEntry)}
                </ul>
            </div>
        </div>
    );
}

let kindToView = {
    feed: feedView,
};

let Home = function(model, mc) {
    ff.log('model', model);
    let view = kindToView[model['kind']];
    if (view === undefined) {
        view = defaultHome;
    }
    return [
        <div id="header" key="header">
            <form onSubmit={mc(onSubmit)}>
                <Input type="text"
                       placeholder="incoming!"
                       value={model['input'] || ""}
                       onChange={mc(ff.set('input'))} />
                <Input type="submit" value="🚀" />
            </form>
        </div>,
        view(model['output'], mc)
    ];
}


let onSignIn = function(app, model) {
    return async function(event) {
        event.preventDefault();
        let data = {
            username: model['signin-username'],
            password: model['signin-password'],
        };
        let response = await ff.post('/api/account/login', data);
        if(response.status === 200) {
            let token = (await response.json())['token'];
            ff.setToken(token);
            return await ff.redirect(app, model.set('%token', token), '/home')
        }
        return await ff.redirect(app, model, '/');
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

class Input extends React.Component {
    constructor(props, ...args) {
        super(props, ...args);
        this.state = { value: props.value };
    }

    componentWillReceiveProps(nextProps) {
        if (this.state.value !== nextProps.value) {
            this.setState({ value: nextProps.value });
        }
    }

    onChange(event) {
        event.persist();
        this.setState({ value: event.target.value }, () => this.props.onChange(event));
    }

    render() {
        return (<input {...this.props} {...this.state} onChange={this.onChange.bind(this)} />);
    }
}

let Index = function(model, mc) {
    ff.log('model', model);
    return (
        <div id="container">
            <div id="enter">
                <h2>Sign In</h2>
                <form onSubmit={mc(onSignIn)}>
                    <p><Input type="text"
                              placeholder="username"
                              value={model['signin-username'] || ""}
                              onChange={mc(ff.set('signin-username'))}/></p>
                    {getErrorMessage('signin-username', model)}
                    <p><Input type="password"
                              placeholder="password"
                              value={model['signin-password'] || ""}
                              onChange={mc(ff.set('signin-password'))}/></p>
                    {getErrorMessage('signin-password', model)}
                    <p><Input type="submit" value="submit" onClick={mc(onSignIn)}/></p>
                    {getErrorMessage('signin-form', model)}
                </form>
                <h2>Sign Up</h2>
                <form onSubmit={mc(onSignUp)}>
                    <p><Input type="text"
                              placeholder="username"
                              value={model['signup-username'] || ""}
                              onChange={mc(ff.set('signup-username'))}/></p>
                    {getErrorMessage('signup-username', model)}
                    <p><Input type="password"
                              placeholder="password"
                              value={model['signup-password'] || ""}
                              onChange={mc(ff.set('signup-password'))}/></p>
                    {getErrorMessage('signup-password', model)}
                    <p><Input type="password"
                              placeholder="validation"
                              value={model['signup-validation'] || ""}
                              onChange={mc(ff.set('signup-validation'))}/></p>
                    {getErrorMessage('signup-validation', model)}
                    <p><Input type="submit" value="submit" onSubmit={mc(onSignUp)}/></p>
                    {getErrorMessage('signup-form', model)}
                </form>
            </div>
        </div>
    );
}



let router = new ff.Router();
router.append('/', ff.routeClean, Index);
router.append('/home', check, Home);




ff.createApp(router);

registerServiceWorker();
