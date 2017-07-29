import React from 'react';
import ReactDOM from 'react-dom';
import { fromJS } from 'immutable';

import { FormGroup, Input, FormFeedback, FormText } from 'reactstrap';


var createAppBase = function(root, init, view) {
  var model = init();

  var render;

  /* wraps event handlers to create controllers.

     The returned function will use the function returned
     by the controller to update the model and trigger a render
     if needed.
   */
  var makeController = function(controller) {
    return function(event) {
      // XXX: This might be performance bottleneck
      // https://fb.me/react-event-pooling
      // XXX: it's possible to avoid this but it will lead to more confusing code
      event.persist()
      var promise = controller(model)(event);
      promise.then(function(transformer) {
        if(transformer) {
          var newModel = transformer(model);
          if (newModel !== model) {
            // XXX: side effect
            model = newModel;
            render();
          }
        }
      });
    }
  };

  /* Render the application */
  render = function() {
    var html = view({model: model, mc: makeController});
    ReactDOM.render(html, root);
  };

  // sneak into an application from the outside.
  return function(change) {
    var promise = change(model);
    promise.then(function(transformer) {
      if(transformer) {
        var newModel = transformer(model);
        if (newModel !== model) {
          // XXX: side effect
          model = newModel;
          render();
        }
      }
    });
  };
};

/* URL Router */

/* FIXME: there is no need to export the router,
 instead use an Array of Array of arguments to pass
 to Router.append */
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

  async resolve(model) {
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

        // pass a transient model to route init.
        model = model.set('%location', location);
        var transformer = await route.init(model);

        // always keep the location in the final model
        // eslint-disable-next-line
        return (model) => transformer(model).set('%location', location);
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
  return function(model) {
    return async function(event) {
      event.preventDefault();
      window.history.pushState({}, "", href);
      var router = model.get('%router');
      var transformer = router.resolve(model);
      window.scrollTo(0, 0);
      return transformer;
    }
  }
}

var redirect = async function(model, href) {
  window.history.pushState({}, "", href);
  var router = model.get('%router');
  var transformer = await router.resolve(model);
  window.scrollTo(0, 0);
  return transformer;
}

var Link = function({mc, href, children}) {
  return <a href={href} onClick={mc(linkClicked(href))}>{children}</a>;
}

var clean = async function(model) {
  return function(model) {
    var newModel = fromJS({});
    // only keep things that start with %
    model.keySeq()
         .filter((x) => x.startsWith('%'))
         .forEach(function(key) {
           newModel = newModel.set(key, model.get(key));
         });
    return newModel;
  }
}

var saveAs = function(name) {
  return function(model) {
    return async function (event) {
      return (model) => model.set(name, event.target.value);
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

// FIXME: workaround the fact that Input is already defined in the module
// once that issue https://github.com/reactstrap/reactstrap/issues/517
// is fixed it will not be necessary to do that.
var out = {
  Link,
  Router,
  Title,
  clean,
  createApp,
  redirect,
  saveAs,
  fromJS,
};


out.Input = function({label, text, error, onChange, type}) {
  var state, feedback;
  if (error) {
    state = "danger";
    feedback = <FormFeedback>{error}</FormFeedback>;
  } else {
    state = undefined;
    feedback = '';
  }
  text = text ? <FormText color="muted">{text}</FormText> : "";
  return (
    <FormGroup color={state}>
        <Input type={type} state={state} onChange={onChange} placeholder={label}/>
        {feedback}
        {text}
    </FormGroup>
  );
}

export default out;
