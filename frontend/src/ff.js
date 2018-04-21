import React from 'react';
import ReactDOM from 'react-dom';
import Immutable from 'seamless-immutable';


/**
 * Neat debug function
 */
let log = function() {
    let args = Array.prototype.slice.call(arguments);
    if (process.env.NODE_ENV !== 'production') {
        console.log.apply(console, args);
    }
    return args[args.length - 1];
}

/**
 * Create base app environment
 *
 * This is useful in context where you don't plan to have
 * a router or websockets
 *
 * @param {app} can be any JavaScript Object it's passed around
 *              the environment. Things that can not be serialized.
 *              It's not required to be immutable.
 * @param {root} is DOM node that is used to render the graphical
 *               part of the application
 * @param {init} is function that must return the seed model.
 *               It usually return an immutable object.
 * @param {view} is a function that takes as argument `app` and
 *               the current `model` and `makeController` usually
 *               simply called `mc`.
 * @returns {Function} called `change` that allows to sneak into
 *                     the application environment from the outside.
 *                     It's useful to extend the behavior of forward.
 */
let createAppBase = function(app, root, init, view) {
    let model = init();

    let render;

    /* wraps event handlers to create controllers.

       The returned function will use the function returned
       by the controller to update the model and trigger a render
       if needed.
     */
    let makeController = function(controller) {
        return function(event) {
            // XXX: This might be performance bottleneck
            // https://fb.me/react-event-pooling
            event.persist()
            let promise = controller(app, model)(event);
            promise.then(function(transformer) {
                // XXX: if the controller returns nothing
                // this will lead to an 'undefined' error
                // which is not very friendly.
                let newModel = transformer(app, model);
                model = newModel;  // XXX: side effect
                render();
            });
        }
    };

    /* Render the application */
    render = function() {
        log('rendering');
        let html = view(model, makeController);
        ReactDOM.render(html, root);
    };

    // sneak into an application from the outside.
    return function(change) {
        let promise = change(app, model);
        promise.then(function(transformer) {
            if(transformer) {
                let newModel = transformer(app, model);
                model = newModel;  // XXX: side effect
                render();
            }
        });
    };
};

/* URL Router */

let Router = class {
    constructor() {
        this.routes = [];
        this.route = undefined;
    }

    append(pattern, init, view) {
        if(!pattern.startsWith('/')) {
            throw new Error("Pattern must start with a /");
        }

        this.routes.push({pattern: pattern, init:init, view: view});
    }

    async resolve(app, model) {
        log('resolving route...');
        let path = document.location.pathname.split('/');
        let match, params;

        for(let index=0; index<this.routes.length; index++) {
            let route = this.routes[index];
            [match, params] = this.match(route, path);

            if (match) {
                this.route = route;
                log('router matched route', route)
                let transformer = await route.init(app, model, params);
                // eslint-disable-next-line
                return _ => transformer(app, model);
            }
        }

        // FIXME: replace with 404 error page
        throw new Error('no matching route found');
    }

    match(route, path) {
        // FIXME: do that at init time
        let pattern = route.pattern.split("/");

        // fast path: if pattern and path are not the same length
        // they can not match
        if (pattern.length !== path.length) {
            return [false, {}];
        }

        // try to match
        let params = {};
        for (var index=0; index < pattern.length; index++) {
            let component = pattern[index];
            if (component.startsWith('{') && component.endsWith('}')) {
                params[component.slice(1, -1)] = path[index];
            } else if (component !== path[index]) {
                return [false, {}]
            } else {
                continue;
            }
        }

        return [true, params];
    }
}

/**
 * Create the app environment, run the app and return a function that allows
 * to sneak into it.
 *
 * @param {container_id} the html identifier of the dom element where to
 *        render the application.
 * @param {router} a Router instance.
 * @returns {Function} a function that allows to sneak into the app closure
 *          from the outside world.
 */
let createApp = function(router) {
    let app = {router: router};

    // prepare createAppBase arguments
    let root = document.getElementById("root");
    let init = function() { return Immutable({}); };
    let view = function(model, mc) {
        return router.route.view(model, mc);
    };

    let change = createAppBase(app, root, init, view);

    window.onpopstate = function(event) {
        return change(router.resolve.bind(router));
    };

    log('initial rendering');
    change(router.resolve.bind(router)); // trigger a render

    return change;
}

let linkClicked = function(href) {
    return function(app, model) {
        return async function(event) {
            event.preventDefault();
            window.history.pushState({}, "", href);
            let transformer = app.router.resolve(app, model);
            window.scrollTo(0, 0);
            return transformer;
        }
    }
}

let redirect = async function(app, model, href) {
    log('redrecting...', app, model, href);
    window.history.pushState({}, "", href);
    let transformer = await app.router.resolve(app, model);
    window.scrollTo(0, 0);
    return transformer;
}

let Link = function({mc, href, children, className}) {
    return <a href={href} onClick={mc(linkClicked(href))} className={className}>{children}</a>;
}

let clean = function(model) {
    let newModel = Immutable({});
    // only keep things that start with %
    Object.keys(model)
          .filter((x) => x.startsWith('%'))
          .forEach(function(key) {
              newModel = newModel.set(key, model[key]);  // XXX: side-effect
          });
    return newModel;
}


let routeClean = async function(app, model) {
    return (app, model) => clean(model);
}

let set = function(name) {
    return function(app, model) {
        return async function (event) {
            let value = event.target.value;
            return (app, model) => model.set(name, value);
        }
    }
}

class Title extends React.Component {
    constructor(props) {
        super(props);
        this.title = props.title;
    }

    componentDidMount() {
        document.title = this.props.title;
    }

    componentDidUpdate() {
        document.title = this.props.title;
    }

    render() {
        // FIXME: with react 16 is not required to return something
        return <div/>;
    }
}

let get = function(path, token) {
    let request = new Request(path);
    if (token) {
        request.headers.set('X-AUTH-TOKEN', token)
    }
    return fetch(request);
}

let post = function(path, data, token) {
    let request = new Request(path, {method: 'POST', body: JSON.stringify(data)});
    if (token) {
        request.headers.set('X-AUTH-TOKEN', token);
    }
    return fetch(request);
}

/**
 *  Get the auth token from the model or localStorage
 */
let getToken = function(model) {
    return model['%token'] || window.localStorage.getItem('%token');
}

let setToken = function(token) {
    window.localStorage.setItem('%token', token);
}

let LogoutClicked = function(app, model) {
    return async function(event) {
        window.localStorage.removeItem('%token');
        return await redirect(app, model, '/');
    }
}

let Logout = function({mc}) {
    return <span id="logout" onClick={mc(LogoutClicked)}>Logout</span>;
}

export default {
    Immutable,
    Link,
    Logout,
    Router,
    Title,
    clean,
    createApp,
    get,
    getToken,
    setToken,
    log,
    post,
    redirect,
    set,
    routeClean,
};
