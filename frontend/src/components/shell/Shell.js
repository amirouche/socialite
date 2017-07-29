import React from 'react';
import './Shell.css';

// import fw from '../../forward.js';


var Shell = function({ children, mc}) {
  return (
    <div id="shell">
        <div id="shell-container">
            { children }
        </div>
    </div>
  );
}

export default Shell;
