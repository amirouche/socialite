import React from 'react';
import ReactDOM from 'react-dom';
import { fromJS } from 'immutable';

import * as rs from 'reactstrap';


let createAppBase = function(root, init, view) {
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
      let promise = controller(model)(event);
      promise.then(function(transformer) {
        // XXX: if the controller returns nothing
        // this will lead to an 'undefined' error
        // which is not very friendly.
        let newModel = transformer(model);
        if (newModel !== model) {
          model = newModel;  // XXX: side effect
          render();
        }
      });
    }
  };

  /* Render the application */
  render = function() {
    let html = view(model, makeController);
    ReactDOM.render(html, root);
  };

  // sneak into an application from the outside.
  return function(change) {
    let promise = change(model);
    promise.then(function(transformer) {
      if(transformer) {
        let newModel = transformer(model);
        if (newModel !== model) {
          model = newModel;  // XXX: side effect
          render();
        }
      }
    });
  };
};

/* URL Router */

let Router = class {
  constructor() {
    this.routes = [];
  }

  append(pattern, init, view) {
    if(!pattern.startsWith('/')) {
      throw new Error("Pattern must start with a /");
    }

    this.routes.push({pattern: pattern, init:init, view: view});
  }

  async resolve(model) {
    let path = document.location.pathname.split('/');
    let match, params;

    for(let index=0; index<this.routes.length; index++) {
      let route = this.routes[index];
      [match, params] = this.match(route, path);

      if (match) {
        let location = fromJS({
          pattern: route.pattern,
          view: route.view,
          params: params
        });

        // pass a transient model to route init.
        model = model.set('%location', location);
        let transformer = await route.init(model);
        
        // Use the model passed to resolve, so that code up
        // the stack has a chance to change the model before
        // a redirect.
        // eslint-disable-next-line
        return _ => transformer(model);
      }
    }

    // FIXME: replace with 404 error page
    throw new Error('no matching route found');
  }

  match(route, path) {
    // FIXME: do that at init time
    let pattern = route.pattern.split("/");

    // if pattern and path are not the same length
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
 * @param {router} a {Router} instance.
 * @returns {Function} a function that allows to sneak into the app closure
 *          from the outside world.
 */
let createApp = function(container_id, router) {
  // prepare createAppBase arguments
  let root = document.getElementById(container_id);
  let init = function() { return fromJS({'%router': router}) };
  let view = function({model, mc}) {
    return model.getIn(['%location', 'view'])({model, mc});
  }

  let change = createAppBase(root, init, view);

  window.onpopstate = function(event) { return change(router.resolve.bind(router)); };

  change(router.resolve.bind(router)); // trigger a render

  return change;
}

let linkClicked = function(href) {
  return function(model) {
    return async function(event) {
      event.preventDefault();
      window.history.pushState({}, "", href);
      let router = model.get('%router');
      let transformer = router.resolve(model);
      window.scrollTo(0, 0);
      return transformer;
    }
  }
}

let redirect = async function(model, href) {
  window.history.pushState({}, "", href);
  let router = model.get('%router');
  let transformer = await router.resolve(model);
  window.scrollTo(0, 0);
  return transformer;
}

let Link = function({mc, href, children, className}) {
  return <a href={href} onClick={mc(linkClicked(href))} className={className}>{children}</a>;
}

let clean = async function(model) {
  return function(model) {
    let newModel = fromJS({});
    // only keep things that start with %
    model.keySeq()
         .filter((x) => x.startsWith('%'))
         .forEach(function(key) {
           newModel = newModel.set(key, model.get(key));  // XXX: side-effect
         });
    return newModel;
  }
}

let saveAs = function(name) {
  return function(model) {
    return async function (event) {
      let value = event.target.value;
      // FIXME: pass name as an array and use model.setIn
      return model => model.set(name, value);
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
  return model.get('%token') || window.localStorage.getItem('%token');
}

let Input = function({label, text, error, onChange, type}) {
  let state, feedback;
  if (error) {
    state = "danger";
    feedback = <rs.FormFeedback>{error}</rs.FormFeedback>;
  } else {
    state = undefined;
    feedback = '';
  }
  text = text ? <rs.FormText color="muted">{text}</rs.FormText> : "";
  return (
    <rs.FormGroup color={state}>
      <rs.Input type={type} state={state} onChange={onChange} placeholder={label}/>
      {feedback}
      {text}
    </rs.FormGroup>
  );
}


export default {
  Link,
  Router,
  Title,
  clean,
  createApp,
  redirect,
  saveAs,
  fromJS,
  get,
  post,
  getToken,
  Input,
};
