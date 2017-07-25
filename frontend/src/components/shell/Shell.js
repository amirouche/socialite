import React from 'react';
import './Shell.css';

import { Link } from '../../forward.js';


var Shell = function({ children, mc}) {
  return (
    <div id="shell">
        <div id="shell-header">
            <h1><Link mc={mc} href="/">Socialite</Link></h1>
            <ul id="shell-header-menu">
                <li><Link mc={mc} href="/bookmarks">Bookmarks</Link></li>
                <li><Link mc={mc} href="/forum">Forum</Link></li>
                <li><Link mc={mc} href="/messaging">Messaging</Link></li>
                <li><Link mc={mc} href="/search">Search</Link></li>
                <li><Link mc={mc} href="/wiki">Wiki</Link></li>
            </ul>
        </div>
        <div id="shell-container">
            { children }
        </div>
    </div>
  );
}

export default Shell;
