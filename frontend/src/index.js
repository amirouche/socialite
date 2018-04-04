import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import registerServiceWorker from './registerServiceWorker';
import ff from './ff.js';


let Home = function(model) {
    return [
        <div id="header">
            <h1>incoming [999+]</h1>
            <p><span role="img">🚀</span></p>
        </div>,
        <div id="container">
            <div class="directory">
                <p class="name">Programming</p>
                <p class="updates">linux.org, hackernews, journal du hacker</p>
                <p class="toolbox"><span rol="img">✓</span></p>
            </div>
            <div class="directory open">
                <h2 class="name">Programming</h2>
                <ul>
                    <li>ff.js yet another javascript framework (github.com)</li>
                    <li>aiohttp the win-win python framework (python.org)</li>
                    <li class="open">
                        <div>
                            <h3>incoming feed reader from space <small>(hyperdev.fr)</small></h3>
                            <p>lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet</p>
                            <p>lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet</p>
                            <p>lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet</p>
                            <p>lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet lorem ipsum dolore sit amet</p>
                        </div>
                    </li>
                    <li>scheme todomvc app (github.com)</li>
                </ul>
            </div>
            <div class="directory">
                <p class="name">Programming</p>
                <p class="updates">linux.org, hackernews, journal du hacker</p>
                <p class="toolbox"><span rol="img">✓</span></p>
            </div>
            <div class="directory">
                <p class="name">Programming</p>
                <p class="updates">linux.org, hackernews, journal du hacker</p>
                <p class="toolbox"><span rol="img">✓</span></p>
            </div>
        </div>
    ];
}

let router = new ff.Router();
router.append('/home', ff.clean, Home);



ff.createApp(router);

registerServiceWorker();
