import React from 'react';
import './Shell.css';

import fw from '../../forward.js';


var Shell = function({ children, mc}) {
  return (
    <div id="shell">
        <div id="shell-header">
            <h1><fw.Link mc={mc} href="/">Socialite</fw.Link></h1>
            <ul id="shell-header-menu">
                <li><fw.Link mc={mc} href="/bookmarks">Bookmarks</fw.Link></li>
                <li><fw.Link mc={mc} href="/forum">Forum</fw.Link></li>
                <li><fw.Link mc={mc} href="/messaging">Messaging</fw.Link></li>
                <li><fw.Link mc={mc} href="/search">Search</fw.Link></li>
                <li><fw.Link mc={mc} href="/wiki">Wiki</fw.Link></li>
            </ul>
        </div>
        <div id="shell-container">
            { children }
        </div>
    </div>
  );
}

export default Shell;
