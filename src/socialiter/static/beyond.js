import './snabbdom.js';
import './snabbdom-attributes.js';
import './snabbdom-eventlisteners.js';

console.log('boot')

var container = document.getElementById('container');

var patch = snabbdom.init([
    snabbdom_attributes.default,
    snabbdom_eventlisteners.default,
]);

var h = snabbdom.h;
var retry = 0;

// TODO: support https/wss
// TOOD: do not hardcode domain
var ws = new WebSocket("ws://localhost:8000/websocket");


/* Translate json to `vnode` using `h` snabbdom helper */
var translate = function(json) {
    var options = {attrs: json.attributes};

    // create callback for each events
    var on = {};
    if(json.on) {
        options.on = {};
        Object.keys(json.on).forEach(function(event_name) {  // TODO: optimize with for-loop
            options.on[event_name] = function(event) {
                var msg = {
                    path: location.pathname,
                    type: 'dom-event',
                    key: json.on[event_name],
                    event: {'target.value': event.target.value},
                    token: localStorage.getItem('token'),
                };
                // console.log('send', msg);
                ws.send(JSON.stringify(msg));
            }
        });
    }

    // recurse to translate children
    var children = json.children.map(function(child) {  // TODO: optimize with a for-loop
        if (child instanceof Object) {
            return translate(child);
        } else { // it's a string or a number
            return child;
        }
    });

    return h(json.tag, options, children);
}

ws.onmessage = function(msg) {
    // console.log('onmessage', msg);
    var msg = JSON.parse(msg.data);
    if (msg.type == 'dom-update') {
        container = patch(container, translate(msg.html));
    } else if (msg.type == 'token-update') {
        localStorage.setItem('token', msg.token);
    } else if (msg.type == 'location-update') {
        location.pathname = msg.pathname;
    } else {
        console.log("message not supported", msg);
    }
}

ws.onopen = function () {
    var msg = {
        path: location.pathname,
        type: 'init',
    };
    ws.send(JSON.stringify(msg));
};
