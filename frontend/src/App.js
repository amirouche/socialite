import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

var test = async function() {
  var response = await fetch('/api/status');
  var body = await response.json();
  return body;
}

test().then(function(body) { console.log(arguments); });


class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h2>Welcome to React</h2>
        </div>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
        </p>
      </div>
    );
  }
}

export default App;
