import React from 'react';
// import ReactDOM from 'react-dom';
import * as serviceWorker from './serviceWorker';

import './index.css';
import ff from './ff.js';


let makeQuery = async function(query) {
    let querystring = new URLSearchParams();
    querystring.set('query', query);
    querystring = querystring.toString();
    let response = await ff.get("/api/?" + querystring);
    return response
}

let indexInit = async function(app, model) {
    // Create querystring based on 'query' querystring parameter
    // filter anyother param because security.
    let url = new URL(document.location.href);
    let query = url.searchParams.get('query');
    query = query.trim()

    if (query.length === 0) {
        return (app, model) => ff.Immutable({});
    }

    let response = await makeQuery(query);

    if (response.status !== 200) {
        return (app, model) => ff.Immutable({});
    }

    let json = await response.json();
    return (app, model) => ff.Immutable(json);
}

let HitView = function({hit}) {
    return (
        <a href={hit.url} className="hit">
            <h2>{hit.title}</h2>
            <p className="url">{hit.url}</p>
            <p className="description">{hit.description}</p>
        </a>
    )
}

let onQuery = function(app, model) {
    return async function(event) {
        let querystring = new URLSearchParams();
        querystring.set('query', model.query);
        querystring = querystring.toString();
        return await ff.redirect(app, model, '/?' + querystring);
    }
}


let IndexView = function(model, mc) {
    ff.pk(model);
    let query = model.query ? model.query : "";
    return (
        <div id="container" className="index">
            <h1>socialiter</h1>
            <div className="searchbox">
                <ff.Input type="text" value={query} onChange={mc(ff.set('query'))} />
                <button onClick={mc(onQuery)}>query</button>
            </div>
            <div className="hits">
                {model.hits.map(hit => <HitView key={hit.url} hit={hit} />)}
            </div>
        </div>
    );
}


let router = new ff.Router();
router.append('/', indexInit, IndexView);

ff.createApp(router);


// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
