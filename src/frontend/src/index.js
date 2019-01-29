import React from 'react';
// import ReactDOM from 'react-dom';
import * as serviceWorker from './serviceWorker';

import './index.css';
import ff from './ff.js';


let indexInit = async function(app, model) {
    let response = await ff.get("/api/status/");
    let json = await response.json();
    return (app, model) => ff.Immutable(json);
}

let IndexView = function(model, mc) {
    return (
        <div id="container" className="index">
            <h1>socialiter</h1>
            <div>
                <ff.Input type="text" />
                <button>query</button>
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
