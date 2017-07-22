import React from 'react';
import ReactDOM from 'react-dom';
import { fromJS } from 'immutable';


var createAppBase = function(root, init, view) {
  var model = init();

  var render;

  /* Allow to create a "greenthread" while staying in the app environment */
  var spawn = function(onTimeout, timeout=0) {
    var f = function() {
      var promise = onTimeout({model, spawn});
      promise.then(function(newModel) {
        if(newModel) {
          model = newModel;
          render();
        }
      });
      render();
    };
    return setTimeout(f, timeout);
  };

  /* wraps event handlers to create controllers.

     The returned function will update the current application model
     with the one returned by the event handler and trigger a render.
   */
  var createController = function(controller) {
    return function(event) {
      var promise = controller({model, spawn})(event);
      promise.then(function(newModel) {
        if(newModel) {
          // XXX: side effect, set model to the model returned by the
          // controller
          model = newModel;
          render();
        }
      });
    }
  };

  /* Render the application */
  render = function() {
    var html = view({model: model, mc: createController});
    ReactDOM.render(html, root);
  };

  // sneak into an application from the outside.
  return function(change) {
    var promise = change({model: model, spawn: spawn});
    promise.then(function(newModel) {
      if(newModel) {
        // XXX: side effect
        model = newModel;
        render();
      }
    });
  };
};

/* URL Router */

var Router = class {
  constructor() {
    this.routes = [];
  }

  append(pattern, init, view) {
    if(!pattern.startsWith('/')) {
      throw new Error("Pattern must start with a /");
    }

    this.routes.push({pattern: pattern, init:init, view: view});
  }

  async resolve({model, spawn}) {
    var path = document.location.pathname.split('/');
    var match, params;

    for(var index=0; index<this.routes.length; index++) {
      var route = this.routes[index];
      [match, params] = this.match(route, path);
      if (match) {
        var location = fromJS({
          pattern: route.pattern,
          view: route.view,
          params: params
        });
        model = model.set('%location', location);
        model = await route.init({model, spawn});
        return model;
      }
    }

    // FIXME: replace with 404 error page
    throw new Error('no matching route found');
  }

  match(route, path) {
    var pattern = route.pattern.split("/");

    // if pattern and path are not the same length
    // they can not match
    if (pattern.length !== path.length) {
      return [false, {}];
    }

    // try to match
    var params = {};
    for (var index=0; index < pattern.length; index++) {
      var component = pattern[index];
      if (component.startsWith(':')) {
        params[component.slice(1)] = path[index];
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
var createApp = function(container_id, router) {
  // prepare createAppBase arguments
  var root = document.getElementById(container_id);
  var init = function() { return fromJS({'%router': router}) };
  var view = function({model, mc}) {
    return model.getIn(['%location', 'view'])({model, mc});
  }

  var change = createAppBase(root, init, view);

  window.onpopstate = function(event) { return change(router.resolve.bind(router)); };

  change(router.resolve.bind(router)); // trigger a render

  return change;
}

var linkClicked = function(href) {
  return function({model, spawn}) {
    return async function(event) {
      event.preventDefault();
      window.history.pushState({}, "", href);
      var router = model.get('%router');
      model = router.resolve({model: model, spawn: spawn});
      return model;
    }
  }
}

var redirect = function(model, spawn, href) {
  window.history.pushState({}, "", href);
  var router = model.get('%router');
  model = router.resolve({model: model, spawn: spawn});
  return model;
}

var Link = function({mc, href, children}) {
  return <a href={href} onClick={mc(linkClicked(href))}>{children}</a>;
}

var identityController = async function({model}) {
  return model;
}

var clean = function(model) {
  var newModel = fromJS({});
  newModel = newModel.set('%location', model.get('%location'));
  newModel = newModel.set('%router', model.get('%router'));
  return newModel;
}

var saveValueAs = function(name) {
  return function({model}) {
    return async function (event) {
      return model.set(name, event.target.value);
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
    return <div/>;
  }
}


export {
  Link,
  Router,
  Title,
  clean,
  createApp,
  identityController,
  redirect,
  saveValueAs,
};
