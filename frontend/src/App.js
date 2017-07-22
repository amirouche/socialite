import React from 'react';
import './App.css';

/* 
 * var test = async function() {
 *   var response = await fetch('/api/status');
 *   var body = await response.json();
 *   return body;
 * }
 * 
 * test().then(function(body) { console.log(arguments); });
 * */

var Child = function({children, model, mc}) {
  return <div>{children}</div>
}

var App = function({model, mc}) {
  return (
    <div id="shell">
        <div id="header">
            <Child model={model} mc={mc}>
                some text as child
            </Child>
        </div>
    </div>
  );
}

export default App;
